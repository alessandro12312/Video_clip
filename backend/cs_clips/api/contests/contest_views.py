from django.db.models import Avg, Count, Exists, F, OuterRef, Subquery
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from cs_clips.api.contests.contest_serializers import (
    ContestDetailOutputSerializer,
    ContestListOutputSerializer,
)
from cs_clips.api.videos.video_serializers import VideoOutputSerializer
from cs_clips.models import Contest, Rating, Video, VideoLike
from cs_clips.permissions import OnlyAdminsPermission
from cs_clips.utils.desempate import desempate_ponderato


@extend_schema_view(
    list=extend_schema(
        summary="Lista contest settimanali",
        description="Lista paginata dei contest con filtri tag e is_closed.",
    ),
    retrieve=extend_schema(
        summary="Dettaglio contest",
        description="Ritorna il dettaglio di un contest con winner nested (se chiuso).",
    ),
)
class ContestViewSet(ReadOnlyModelViewSet):
    """ViewSet read-only per listing e dettaglio contest settimanali."""

    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "head", "options", "post"]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["tag", "is_closed"]

    def get_queryset(self):
        return (
            Contest.objects.select_related("winner")
            .annotate(
                video_count=Count("videos"),
            )
            .order_by("-start_date")
        )

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ContestDetailOutputSerializer
        return ContestListOutputSerializer

    @extend_schema(
        summary="Lista video vincitori",
        description="Ritorna la lista paginata dei video vincitori dei contest chiusi.",
        parameters=[
            OpenApiParameter(
                name="page",
                type=int,
                required=False,
                description="Numero della pagina",
            ),
            OpenApiParameter(
                name="page_size",
                type=int,
                required=False,
                description="Numero di risultati per pagina",
            ),
        ],
        responses=VideoOutputSerializer(many=True),
    )
    @action(detail=False, methods=["get"], url_path="winners")
    def winners(self, request):
        """Lista paginata dei video vincitori dei contest chiusi."""
        winners = (
            Video.objects.filter(
                won_contests__is_closed=True,
            )
            .select_related("uploader")
            .order_by("-won_contests__closed_at")
        )

        paginator = PageNumberPagination()
        result_page = paginator.paginate_queryset(winners, request)

        serializer = VideoOutputSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    @extend_schema(
        summary="Video del contest con annotazioni rating",
        description=(
            "Ritorna la lista paginata dei video di un contest, "
            "ordinati per media voti (classifica). Include avg_rating, "
            "my_rating_id e my_rating_value per l'utente corrente."
        ),
        parameters=[
            OpenApiParameter(
                name="page",
                type=int,
                required=False,
                description="Numero della pagina",
            ),
            OpenApiParameter(
                name="page_size",
                type=int,
                required=False,
                description="Numero di risultati per pagina",
            ),
        ],
        responses=VideoOutputSerializer(many=True),
    )
    @action(detail=True, methods=["get"], url_path="videos")
    def videos(self, request, pk=None):
        """Video del contest con annotazioni rating per classifica e votazione."""
        contest = self.get_object()
        qs = (
            Video.objects.filter(contest=contest)
            .select_related("uploader")
            .annotate(
                avg_rating=Avg("ratings__value"),
                like_count=Count("likes", distinct=True),
            )
            .order_by(F("avg_rating").desc(nulls_last=True))
        )

        if request.user.is_authenticated:
            my_rating = Rating.objects.filter(video=OuterRef("pk"), user=request.user)
            qs = qs.annotate(
                my_rating_id=Subquery(my_rating.values("id")[:1]),
                my_rating_value=Subquery(my_rating.values("value")[:1]),
                is_liked_by_me=Exists(
                    VideoLike.objects.filter(video=OuterRef("pk"), user=request.user)
                ),
            )

        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = VideoOutputSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = VideoOutputSerializer(qs, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Chiudi contest attivo",
        description="Chiude il contest attivo per il tag e decreta il vincitore.",
        parameters=[
            OpenApiParameter(
                name="tag",
                description="Tag del contest da chiudere",
                required=True,
                type=str,
                enum=[choice[0] for choice in Contest.Tag.choices],
            )
        ],
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="end",
        permission_classes=[OnlyAdminsPermission],
    )
    def end(self, request):
        """Chiude il contest attivo per un tag e decreta il vincitore."""
        valid_tags = [c[0] for c in Contest.Tag.choices]

        tag = (
            (request.data.get("tag") or request.query_params.get("tag") or "")
            .strip()
            .lower()
        )

        if tag not in valid_tags:
            raise ValidationError(
                {"tag": f"Valore non valido. Valori ammessi: {', '.join(valid_tags)}"}
            )

        today = timezone.now().date()

        contest = Contest.objects.filter(
            start_date__lte=today, end_date__gte=today, is_closed=False, tag=tag
        ).first()

        if not contest:
            return Response(
                {"detail": f"Nessun contest attivo per il tag '{tag}'."},
                status=status.HTTP_404_NOT_FOUND,
            )

        videos = Video.objects.filter(contest=contest).annotate(
            avg_rating=Avg("ratings__value")
        )

        if not videos.exists():
            return Response(
                {"detail": "Nessun video presente per questo contest."},
                status=status.HTTP_404_NOT_FOUND,
            )

        avg_rated_videos = [v for v in videos if v.avg_rating is not None]

        if avg_rated_videos:
            max_rating = max(v.avg_rating for v in avg_rated_videos)
            top_videos = [v for v in avg_rated_videos if v.avg_rating == max_rating]
        else:
            if videos.count() == 1:
                winner = videos.first()
                top_videos = [winner]
            else:
                top_videos = list(videos)

        winner = (
            top_videos[0] if len(top_videos) == 1 else desempate_ponderato(top_videos)
        )

        contest.winner = winner
        contest.is_closed = True
        closed_at_now = contest.closed_at = timezone.now()
        contest.save()

        winner_data = VideoOutputSerializer(winner).data if winner else None

        finalists_data = (
            [VideoOutputSerializer(v).data for v in top_videos]
            if len(top_videos) > 1
            else None
        )

        return Response(
            {
                "contest": {
                    "id": contest.id,
                    "name": contest.name,
                    "start_date": contest.start_date,
                    "end_date": contest.end_date,
                    "closed_at": closed_at_now,
                    "winner_id": contest.winner.id if contest.winner else None,
                },
                "winner": winner_data,
                "finalists": finalists_data,
            },
            status=status.HTTP_200_OK,
        )
