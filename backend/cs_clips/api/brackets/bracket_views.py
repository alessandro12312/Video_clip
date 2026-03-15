from django.db import IntegrityError, transaction
from django.db.models import Avg, Count, F, Q
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet

from cs_clips.api.brackets.bracket_serializers import (
    BracketDetailOutputSerializer,
    BracketListOutputSerializer,
    ContestEntryNestedSerializer,
    EnterBracketInputSerializer,
    MatchupOutputSerializer,
    VoteMatchupInputSerializer,
)
from cs_clips.models import (
    Bracket,
    ContestEntry,
    Matchup,
    MatchupVote,
    Notification,
    Video,
)
from cs_clips.permissions import OnlyAdminsPermission


@extend_schema_view(
    list=extend_schema(
        summary="Lista bracket",
        description="Lista paginata dei bracket con filtro opzionale per status.",
    ),
    retrieve=extend_schema(
        summary="Dettaglio bracket",
        description="Dettaglio bracket con matchup raggruppati per turno e my_entry.",
    ),
)
class BracketViewSet(ReadOnlyModelViewSet):
    """ViewSet read-only per listing e dettaglio bracket con azione enter."""

    http_method_names = ["get", "post", "head", "options"]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status"]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        return Bracket.objects.annotate(
            entries_count=Count("entries", distinct=True),
        ).select_related("created_by")

    def get_serializer_class(self):
        if self.action == "retrieve":
            return BracketDetailOutputSerializer
        if self.action == "enter":
            return EnterBracketInputSerializer
        return BracketListOutputSerializer

    @extend_schema(
        summary="Iscriviti al bracket",
        description="Iscrive l'utente al bracket con il video specificato.",
        request=EnterBracketInputSerializer,
        responses={201: ContestEntryNestedSerializer},
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="enter",
        permission_classes=[IsAuthenticated],
    )
    def enter(self, request, pk=None):
        bracket = self.get_object()

        if bracket.status != Bracket.Status.REGISTRATION:
            return Response(
                {"detail": "Il bracket non e' in fase di registrazione."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if bracket.entries.count() >= bracket.max_participants:
            return Response(
                {"detail": "Bracket pieno: numero massimo di partecipanti raggiunto."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = EnterBracketInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        video_id = serializer.validated_data["video_id"]

        try:
            video = Video.objects.get(pk=video_id)
        except Video.DoesNotExist:
            return Response(
                {"detail": "Video non trovato."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with transaction.atomic():
                entry = ContestEntry.objects.create(
                    bracket=bracket, user=request.user, video=video
                )
                Notification.objects.create(
                    recipient=request.user,
                    sender=request.user,
                    type="bracket_invite",
                    video=video,
                )
        except IntegrityError:
            return Response(
                {"detail": "Sei gia' iscritto a questo bracket."},
                status=status.HTTP_409_CONFLICT,
            )

        output = ContestEntryNestedSerializer(entry).data
        return Response(output, status=status.HTTP_201_CREATED)


@extend_schema_view(
    retrieve=extend_schema(
        summary="Dettaglio matchup",
        description="Ritorna il dettaglio di un matchup con entry nested e avg_rating.",
    ),
)
class MatchupViewSet(mixins.RetrieveModelMixin, GenericViewSet):
    """ViewSet per dettaglio matchup con azioni vote e close."""

    http_method_names = ["get", "post", "head", "options"]

    def get_permissions(self):
        if self.action == "retrieve":
            return [AllowAny()]
        if self.action == "close":
            return [OnlyAdminsPermission()]
        return [IsAuthenticated()]

    def get_queryset(self):
        return Matchup.objects.select_related(
            "bracket",
            "entry_1__user",
            "entry_1__video",
            "entry_2__user",
            "entry_2__video",
            "winner",
        ).annotate(
            avg_rating_1=Avg("votes__value", filter=Q(votes__entry=F("entry_1"))),
            avg_rating_2=Avg("votes__value", filter=Q(votes__entry=F("entry_2"))),
        )

    def get_serializer_class(self):
        if self.action == "vote":
            return VoteMatchupInputSerializer
        return MatchupOutputSerializer

    @extend_schema(
        summary="Vota matchup",
        description="Registra un voto (1-5) per una entry del matchup.",
        request=VoteMatchupInputSerializer,
        responses={201: None},
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="vote",
        permission_classes=[IsAuthenticated],
    )
    def vote(self, request, pk=None):
        matchup = self.get_object()

        if matchup.is_completed:
            return Response(
                {"detail": "Il matchup e' gia' completato."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = VoteMatchupInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        entry = serializer.validated_data["entry"]
        value = serializer.validated_data["value"]

        if entry not in (matchup.entry_1, matchup.entry_2):
            return Response(
                {"detail": "L'entry non appartiene a questo matchup."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            MatchupVote.objects.create(
                matchup=matchup, user=request.user, entry=entry, value=value
            )
        except IntegrityError:
            return Response(
                {"detail": "Hai gia' votato per questo matchup."},
                status=status.HTTP_409_CONFLICT,
            )

        return Response(
            {"detail": "Voto registrato."},
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(
        summary="Chiudi matchup",
        description="Calcola il vincitore in base alla media voti e avanza il bracket.",
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="close",
        permission_classes=[OnlyAdminsPermission],
    )
    def close(self, request, pk=None):
        matchup = self.get_object()

        if matchup.is_completed:
            return Response(
                {"detail": "Matchup gia' completato."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not matchup.entry_1 or not matchup.entry_2:
            return Response(
                {"detail": "Matchup incompleto."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Calcola medie voti
        votes = matchup.votes.all()
        if not votes.exists():
            return Response(
                {"detail": "Impossibile chiudere: nessun voto registrato."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        agg_1 = votes.filter(entry=matchup.entry_1).aggregate(avg=Avg("value"))
        agg_2 = votes.filter(entry=matchup.entry_2).aggregate(avg=Avg("value"))
        avg_1 = agg_1["avg"] or 0
        avg_2 = agg_2["avg"] or 0

        # Vincitore: media piu' alta, parita' → entry_1 (determinismo FR43b)
        winner = matchup.entry_1 if avg_1 >= avg_2 else matchup.entry_2

        # Chiude matchup e propaga avanzamento
        from cs_clips.utils.bracket_logic import close_matchup

        close_matchup(matchup, winner)

        # Notifica bracket_turn per i partecipanti del prossimo matchup
        next_matchup = matchup.bracket.matchups.filter(
            round_number=matchup.round_number + 1,
            position=matchup.position // 2,
        ).first()
        if next_matchup:
            for entry in [next_matchup.entry_1, next_matchup.entry_2]:
                if entry:
                    Notification.objects.create(
                        recipient=entry.user,
                        type="bracket_turn",
                        sender=request.user,
                        video=entry.video,
                    )

        return Response(
            {"detail": "Matchup chiuso.", "winner_entry_id": winner.id},
            status=status.HTTP_200_OK,
        )
