import logging
from datetime import timedelta

import django_filters
from django.db.models import Avg, F
from django.utils import timezone
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import parsers, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle

from cs_clips.api.videos.video_serializers import (
    VideoInputSerializer,
    VideoOutputSerializer,
    VideoUpdateSerializer,
)
from cs_clips.exceptions.error_handler import handle_exception_with_serializer
from cs_clips.models import Video
from cs_clips.permissions import RoleBasedPermission
from cs_clips.utils.get_date_util import get_or_create_current_contest

logger = logging.getLogger("views")


class VideoFilter(django_filters.FilterSet):
    """Filtro video per uploader ID (NumberFilter per evitare validazione FK)."""

    uploader = django_filters.NumberFilter(field_name="uploader_id")

    class Meta:
        model = Video
        fields = ["uploader"]


class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all().order_by("-created_at")
    permission_classes = [IsAuthenticated, RoleBasedPermission]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]
    filterset_class = VideoFilter

    def get_queryset(self):
        """Queryset con annotazione avg_rating per evitare N+1."""
        return Video.objects.annotate(
            avg_rating=Avg("ratings__value")
        ).order_by("-created_at")

    def get_throttles(self):
        if self.action == "create":
            self.throttle_scope = "upload"
            return [ScopedRateThrottle()]
        return super().get_throttles()

    @extend_schema(
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "maxLength": 100,
                    },
                    "tag": {"$ref": "#/components/schemas/TagEnum"},
                    "file": {"type": "string", "format": "binary"},
                },
            }
        },
        responses=VideoOutputSerializer,
        summary="Crea un nuovo video",
        description="Carica un nuovo video associandolo a un tag "
        "e al contest corrente.",
    )
    def create(self, request, *args, **kwargs):
        logger.info("[video_views] Richiesta creazione video ricevuta")
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer, *args, **kwargs):
        """
        Salva il video e lo associa al contest corrente.
        L'upload fisico del file viene gestito automaticamente dal backend di storage
        (es. MinIO S3), tramite il campo FileField e il serializer.
        """
        logger.info(
            "[video_views] Upload video data: %s, user: %s",
            serializer.validated_data,
            self.request.user,
        )
        tag = self.request.data.get("tag")
        if not tag:
            logger.error(
                "[video_views] Campo 'tag' mancante nella richiesta di upload video"
            )
            raise ValidationError({"tag": "Questo campo è obbligatorio."})
        contest = get_or_create_current_contest(tag)
        if not serializer.is_valid():
            logger.error(f"[video_views] Video upload error: {serializer.errors}")
            raise ValidationError(serializer.errors)
        serializer.save(uploader=self.request.user, contest=contest, tag=tag)
        logger.info("[video_views] Video creato e associato al contest")

    # @action(detail=True, methods=['delete', 'post'], url_path='revert')
    # def revert(self, request, pk=None):
    #     """
    #     Endpoint chiamato da FilePond per annullare un upload.
    #     Cancella il video dal DB e dal backend storage.
    #     """
    #     video = self.get_object()
    #     video.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)

    def update(self, request, *args, **kwargs):
        """
        PUT → input con VideoUpdateSerializer,
        output con VideoOutputSerializer.
        """
        logger.info("[video_views] Richiesta update video ricevuta")
        instance = self.get_object()
        serializer = VideoUpdateSerializer(
            instance, data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        logger.info(f"[video_views] Video ID {instance.id} aggiornato")
        ctx = {"request": request}
        return Response(
            VideoOutputSerializer(instance, context=ctx).data,
            status=status.HTTP_200_OK,
        )

    def partial_update(self, request, *args, **kwargs):
        """
        PATCH → input con VideoUpdateSerializer,
        output con VideoOutputSerializer.
        """
        logger.info("[video_views] Richiesta partial_update video ricevuta")
        instance = self.get_object()
        serializer = VideoUpdateSerializer(
            instance,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        msg = f"[video_views] Video ID {instance.id} aggiornato (parziale)"
        logger.info(msg)
        ctx = {"request": request}
        return Response(
            VideoOutputSerializer(instance, context=ctx).data,
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"], url_path="following")
    def videos_from_following(self, request):
        """
        Restituisce i video caricati dagli utenti che l'utente autenticato segue.
        Ordinati dal più recente al meno recente.
        """
        logger.info("[video_views] Richiesta video utenti seguiti")
        user = request.user

        # Controllo permessi: solo user e superuser SOLO PER TEST
        # if not user.is_authenticated or (
        #     not user.is_superuser and not user.groups.filter(name='user').exists()
        # ):
        #     return Response({'detail': 'Accesso negato. Solo per utenti confermati.'},
        #                     status=status.HTTP_403_FORBIDDEN)

        following_users = user.following.all()

        # Filtra i video caricati dagli utenti seguiti
        videos = Video.objects.filter(uploader__in=following_users).order_by(
            "-created_at"
        )

        # Applica paginazione globale
        page = self.paginate_queryset(videos)
        serializer = self.get_serializer(page or videos, many=True)

        logger.info(
            f"[video_views] Trovati {len(serializer.data)} video dagli utenti seguiti"
        )
        return (
            self.get_paginated_response(serializer.data)
            if page
            else Response(serializer.data)
        )

    # Documentazione OpenAPI per l'endpoint top_rated
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="range",
                description="Intervallo temporale: day, week, month, year, all",
                required=False,
                type=str,
                enum=["day", "week", "month", "year", "all"],
            )
        ]
    )
    # Top rated in base a un intervallo di tempo, controllato
    # da FE per spaziare quando finiscono i video
    @action(detail=False, methods=["get"], url_path="top-rated")
    def top_rated(self, request):
        """
        Restituisce i video top-rated filtrabili per intervallo temporale:
        day, week, month, year, all (default: all).
        """
        range_param = request.query_params.get("range", "all")
        logger.info(f"[video_views] Richiesta top_rated con range: {range_param}")
        now = timezone.now()

        # Calcola l'intervallo di tempo
        time_ranges = {
            "day": now - timedelta(days=1),
            "week": now - timedelta(days=7),
            "month": now - timedelta(days=30),
            "year": now - timedelta(days=365),
            "all": None,
        }

        # Valida parametro
        if range_param not in time_ranges:
            logger.warning(f"[video_views] Intervallo non valido: {range_param}")
            return Response(
                {"detail": f"Intervallo non valido: {range_param}"}, status=400
            )

        queryset = Video.objects.all()
        if time_ranges[range_param]:
            queryset = queryset.filter(created_at__gte=time_ranges[range_param])

        # Calcolo della media voto
        queryset = queryset.annotate(average_rating=Avg("ratings__value")).order_by(
            "-average_rating"
        )

        # Paginazione
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page or queryset, many=True)
        logger.info(f"[video_views] Trovati {len(serializer.data)} video top-rated")
        return (
            self.get_paginated_response(serializer.data)
            if page
            else Response(serializer.data)
        )

    @action(detail=True, methods=["post"], url_path="views", parser_classes=[])
    def views(self, request, pk=None):
        """
        Endpoint per incrementare le visualizzazioni di un video.
        Chiamato dal frontend ogni volta che il video viene
        effettivamente visualizzato. 5/10 secondi da frontend.
        """
        logger.info(f"[video_views] Incremento visualizzazioni per video ID {pk}")
        video = self.get_object()
        video.views = F("views") + 1
        video.save(update_fields=["views"])
        video.refresh_from_db()  # aggiorna il valore da DB
        logger.info(f"[video_views] Nuovo numero di visualizzazioni: {video.views}")
        return Response({"views": video.views}, status=status.HTTP_200_OK)

    def get_serializer_class(self):
        logger.info(
            f"[video_views] Determinazione serializer per action: {self.action}"
        )
        if self.action == "create":
            return VideoInputSerializer
        elif self.action in ["update", "partial_update"]:
            return VideoUpdateSerializer
        return VideoOutputSerializer

    def handle_exception(self, exc):
        logger.error(f"[video_views] Eccezione gestita: {exc}")
        return handle_exception_with_serializer(exc)
