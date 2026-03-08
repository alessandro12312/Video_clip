import logging
import re
from collections import defaultdict
from datetime import timedelta
from pathlib import PurePosixPath

import django_filters
from django.db.models import (
    Avg,
    BooleanField,
    Count,
    Exists,
    F,
    IntegerField,
    OuterRef,
    Subquery,
    Value,
)
from django.utils import timezone
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import parsers, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle

from cs_clips.api.comments.comment_serializers import CommentSerializer
from cs_clips.api.videos.video_serializers import (
    VideoInputSerializer,
    VideoOutputSerializer,
    VideoUpdateSerializer,
)
from cs_clips.exceptions.error_handler import handle_exception_with_serializer
from cs_clips.exceptions.error_response_serializer import ErrorResponseSerializer
from cs_clips.models import Comment, CommentLike, Notification, Rating, Video, VideoLike
from cs_clips.permissions import OnlyUsersPermission, RoleBasedPermission
from cs_clips.utils.get_date_util import get_or_create_current_contest
from cs_clips.utils.notification_helpers import create_notification
from project_clip import settings

logger = logging.getLogger("views")


class VideoFilter(django_filters.FilterSet):
    """Filtro video per uploader ID (NumberFilter per evitare validazione FK)."""

    uploader = django_filters.NumberFilter(field_name="uploader_id")

    class Meta:
        model = Video
        fields = ["uploader"]


class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all().order_by("-created_at")
    http_method_names = ["get", "post", "put", "patch", "delete", "head", "options"]
    permission_classes = [IsAuthenticated, RoleBasedPermission]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]
    filterset_class = VideoFilter

    def get_permissions(self):
        """Retrieve pubblico per SSR (OG tags, condivisione link)."""
        if self.action == "retrieve":
            return [AllowAny()]
        return super().get_permissions()

    def get_queryset(self):
        """Queryset con annotazioni avg_rating, my_rating, like, is_liked."""
        qs = Video.objects.annotate(
            avg_rating=Avg("ratings__value"),
            like_count=Count("likes", distinct=True),
        ).order_by("-created_at")
        if self.request.user.is_authenticated:
            my_rating_qs = Rating.objects.filter(
                video=OuterRef("pk"), user=self.request.user
            )
            qs = qs.annotate(
                my_rating_id=Subquery(my_rating_qs.values("id")[:1]),
                my_rating_value=Subquery(my_rating_qs.values("value")[:1]),
                is_liked_by_me=Exists(
                    VideoLike.objects.filter(
                        video=OuterRef("pk"), user=self.request.user
                    )
                ),
            )
        else:
            qs = qs.annotate(
                my_rating_id=Value(None, output_field=IntegerField()),
                my_rating_value=Value(None, output_field=IntegerField()),
                is_liked_by_me=Value(False, output_field=BooleanField()),
            )
        return qs

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
                    "allow_download": {
                        "type": "boolean",
                        "default": True,
                    },
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
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        instance = serializer.instance
        ctx = {"request": request}
        output = VideoOutputSerializer(instance, context=ctx)
        headers = self.get_success_headers(output.data)
        return Response(
            output.data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

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
        tag = serializer.validated_data["tag"]
        contest = get_or_create_current_contest(tag)
        serializer.save(uploader=self.request.user, contest=contest)
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
        following_users = user.following.all()

        # Usa get_queryset() per ereditare annotazione avg_rating (evita N+1)
        videos = self.get_queryset().filter(uploader__in=following_users)

        # page is not None distingue "paginazione applicata (anche vuota)"
        # da "nessun paginatore configurato"
        page = self.paginate_queryset(videos)
        serializer = self.get_serializer(
            page if page is not None else videos, many=True
        )

        logger.info(
            "[video_views] Trovati %s video dagli utenti seguiti",
            len(serializer.data),
        )
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

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

        queryset = self.get_queryset()
        if time_ranges[range_param]:
            queryset = queryset.filter(created_at__gte=time_ranges[range_param])

        # Riordina per media voto (avg_rating già annotato da get_queryset)
        queryset = queryset.order_by(F("avg_rating").desc(nulls_last=True))

        # Paginazione — page is not None (non "if page") per gestire pagine vuote
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(
            page if page is not None else queryset, many=True
        )
        logger.info(f"[video_views] Trovati {len(serializer.data)} video top-rated")
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

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

    @staticmethod
    def _sanitize_filename(title, original_path):
        """Sanitizza il titolo per uso in Content-Disposition header."""
        ext = PurePosixPath(original_path).suffix or ".mp4"
        # Rimuovi caratteri non sicuri per header HTTP
        safe_title = re.sub(r"[^\w \-.]", "", title).strip()
        if not safe_title:
            safe_title = "clip"
        return f"{safe_title}{ext}"

    @extend_schema(
        summary="Download clip",
        description="Genera presigned URL per il download della clip. "
        "Il proprietario può sempre scaricare, "
        "altri utenti solo se allow_download=True.",
        responses={
            200: {
                "type": "object",
                "properties": {"download_url": {"type": "string"}},
            },
            403: {
                "type": "object",
                "properties": {"detail": {"type": "string"}},
            },
        },
    )
    @action(
        detail=True,
        methods=["get"],
        url_path="download",
        permission_classes=[IsAuthenticated, OnlyUsersPermission],
    )
    def download(self, request, pk=None):
        """Genera presigned URL con Content-Disposition: attachment per il download."""
        video = self.get_object()

        # Il proprietario può SEMPRE scaricare
        if video.uploader != request.user and not video.allow_download:
            return Response(
                {"detail": "Il download non è abilitato per questa clip"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Genera presigned URL con Content-Disposition: attachment
        safe_filename = self._sanitize_filename(video.title, video.file.name)
        client = VideoOutputSerializer._get_minio_client()
        download_url = client.presigned_get_object(
            settings.MINIO_STORAGE_MEDIA_BUCKET_NAME,
            video.file.name,
            expires=timedelta(hours=1),
            response_headers={
                "response-content-disposition": (
                    f'attachment; filename="{safe_filename}"'
                )
            },
        )

        return Response({"download_url": download_url})

    @extend_schema(
        request=None,
        responses={
            201: {"type": "object", "properties": {"detail": {"type": "string"}}},
            204: None,
            404: ErrorResponseSerializer,
            409: ErrorResponseSerializer,
        },
        summary="Like/unlike un video",
        description="POST per mettere like, DELETE per rimuovere il like.",
    )
    @action(
        detail=True,
        methods=["post", "delete"],
        url_path="like",
        permission_classes=[IsAuthenticated, OnlyUsersPermission],
    )
    def like(self, request, pk=None):
        """Mette o rimuove like a un video."""
        video = self.get_object()
        if request.method == "POST":
            VideoLike.objects.create(user=request.user, video=video)
            create_notification(
                recipient=video.uploader,
                sender=request.user,
                type=Notification.Type.LIKE_RECEIVED,
                video=video,
            )
            return Response(
                {"detail": "Like aggiunto."}, status=status.HTTP_201_CREATED
            )
        # DELETE
        deleted, _ = VideoLike.objects.filter(user=request.user, video=video).delete()
        if not deleted:
            raise NotFound("Like non trovato.")
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        summary="Popup comments per video",
        description="Ritorna il commento con più like per ogni timestamp_second "
        "(soglia minima: 1 like). Commenti disabilitati esclusi.",
        responses={200: CommentSerializer(many=True)},
    )
    @action(detail=True, methods=["get"], url_path="popup-comments")
    def popup_comments(self, request, pk=None):
        """Ritorna i commenti popup: per ogni timestamp, il più likato (≥1 like)."""
        video = self.get_object()

        # Query: commenti attivi con timestamp > 0 e almeno 1 like
        qs = (
            Comment.objects.filter(
                video=video,
                is_disabled=False,
                timestamp_second__gt=0,
            )
            .annotate(like_count=Count("likes", distinct=True))
            .filter(like_count__gte=1)
        )

        # Annota is_liked_by_me per utente autenticato
        if request.user.is_authenticated:
            qs = qs.annotate(
                is_liked_by_me=Exists(
                    CommentLike.objects.filter(
                        comment=OuterRef("pk"), user=request.user
                    )
                ),
            )
        else:
            qs = qs.annotate(
                is_liked_by_me=Value(False, output_field=BooleanField()),
            )

        # Raggruppa per timestamp_second: tieni il top-liked (parità → più recente)
        by_ts = defaultdict(list)
        for comment in qs:
            by_ts[comment.timestamp_second].append(comment)

        popup_comments = []
        for ts in sorted(by_ts.keys()):
            top = max(by_ts[ts], key=lambda c: (c.like_count, c.created_at))
            popup_comments.append(top)

        serializer = CommentSerializer(
            popup_comments, many=True, context={"request": request}
        )
        return Response(serializer.data)

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
