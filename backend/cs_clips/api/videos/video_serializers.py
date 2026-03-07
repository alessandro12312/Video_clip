# Video serializer
import logging
import tempfile
import uuid
from datetime import timedelta
from functools import lru_cache
from pathlib import Path

from django.core.files import File as DjangoFile
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from drf_spectacular.utils import extend_schema_field
from minio import Minio
from moviepy import VideoFileClip
from rest_framework import serializers

from cs_clips.models import Video
from cs_clips.utils.get_date_util import get_or_create_current_contest
from project_clip import settings

logger = logging.getLogger("serializers")


class VideoOutputSerializer(serializers.ModelSerializer):
    uploader = serializers.ReadOnlyField(source="uploader.username")
    average_rating = serializers.SerializerMethodField()
    file = serializers.FileField(read_only=True, help_text="URL del file video.")
    file_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    my_rating_id = serializers.IntegerField(
        read_only=True, allow_null=True, default=None
    )
    my_rating_value = serializers.IntegerField(
        read_only=True, allow_null=True, default=None
    )

    class Meta:
        model = Video
        fields = (
            "id",
            "title",
            "duration",
            "file",
            "file_url",
            "thumbnail_url",
            "uploader",
            "average_rating",
            "views",
            "created_at",
            "updated_at",
            "contest",
            "tag",
            "allow_download",
            "my_rating_id",
            "my_rating_value",
        )
        read_only_fields = (
            "id",
            "duration",
            "created_at",
            "updated_at",
            "uploader",
            "contest",
            "views",
            "average_rating",
            "file",
            "file_url",
            "thumbnail_url",
            "allow_download",
            "my_rating_id",
            "my_rating_value",
        )

    @extend_schema_field(serializers.FloatField)
    def get_average_rating(self, obj):
        # Usa annotazione avg_rating dal queryset (evita N+1)
        if hasattr(obj, "avg_rating"):
            return round(obj.avg_rating, 2) if obj.avg_rating is not None else 0.0
        # Fallback per istanze senza annotazione (retrieve singolo, custom actions)
        ratings = obj.ratings.all()
        if not ratings.exists():
            return 0.0
        return round(sum(r.value for r in ratings) / ratings.count(), 2)

    @staticmethod
    @lru_cache(maxsize=1)  # evita di ricreare il client ad ogni chiamata
    def _get_minio_client() -> Minio:
        """
        Restituisce un singleton di Minio client inizializzato
        con i parametri definiti in settings.py.
        """

        logger.info("[video_serializer] Inizializzazione Minio client singleton")

        return Minio(
            endpoint=settings.MINIO_STORAGE_ENDPOINT,
            access_key=settings.MINIO_STORAGE_ACCESS_KEY,
            secret_key=settings.MINIO_STORAGE_SECRET_KEY,
            secure=settings.MINIO_STORAGE_USE_HTTPS,
        )

    @extend_schema_field(serializers.URLField(allow_null=True))
    def get_thumbnail_url(self, obj):
        """Genera presigned URL per il thumbnail, se esiste."""
        if not obj.thumbnail:
            return None
        try:
            client = self._get_minio_client()
            return client.presigned_get_object(
                settings.MINIO_STORAGE_MEDIA_BUCKET_NAME,
                obj.thumbnail.name,
                expires=timedelta(hours=1),
            )
        except Exception as e:
            logger.warning(
                "[video_serializer] Impossibile generare presigned URL "
                "per thumbnail video ID %s: %s",
                obj.id,
                e,
            )
            return None

    def get_file_url(self, obj):
        """
        Genera una presigned-URL valida **1 ora** dal bucket MinIO
        indicato in settings.
        Se MinIO non risponde restituisce l'URL locale,
        così evitiamo un 500 e diamo comunque un link al client.
        """

        logger.info(
            f"[video_serializer] Generazione presigned URL per video ID {obj.id}"
        )

        if not obj.file:
            logger.warning(
                f"[video_serializer] Nessun file associato al video ID {obj.id}"
            )
            return None

        bucket_name = settings.MINIO_STORAGE_MEDIA_BUCKET_NAME
        object_name = obj.file.name
        client = self._get_minio_client()
        return client.presigned_get_object(
            bucket_name, object_name, expires=timedelta(hours=1)
        )


class VideoInputSerializer(serializers.ModelSerializer):
    ALLOWED_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
    ALLOWED_CONTENT_TYPES = {
        "video/mp4",
        "video/quicktime",
        "video/x-msvideo",
        "video/x-matroska",
        "video/webm",
    }
    MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB

    # DRF BooleanField.initial=False tratta assenza campo come False
    # in multipart — serve default esplicito per preservare il model default
    allow_download = serializers.BooleanField(default=True, required=False)

    class Meta:
        model = Video
        fields = ("title", "file", "tag", "allow_download")

    # TODO rivedi come genera il contest
    def create(self, validated_data):
        """
        Crea un Video:
        1. Valida formato/dimensione del file uploadato.
        2. Scrive il file su disco temp se InMemoryUploadedFile.
        3. Usa MoviePy/Ffmpeg per estrarne durata e thumbnail.
        4. Valida la durata (10s – 60s).
        5. Salva il modello Video in DB.
        6. Allega il thumbnail generato (graceful fallback se fallisce).
        """
        uploaded_file = validated_data.get("file")
        logger.info(f"[video_serializer] Tipo file ricevuto: {type(uploaded_file)}")

        if not uploaded_file:
            logger.error("[video_serializer] File non fornito.")
            raise serializers.ValidationError({"file": "File non fornito."})

        # ----- Validazione formato e dimensione (prima di MoviePy) -----
        ext = Path(uploaded_file.name).suffix.lower()
        if ext not in self.ALLOWED_EXTENSIONS:
            raise serializers.ValidationError(
                "Formato non supportato. Formati accettati: MP4, MOV, AVI, MKV, WebM"
            )
        if uploaded_file.content_type not in self.ALLOWED_CONTENT_TYPES:
            raise serializers.ValidationError(
                "Formato non supportato. Formati accettati: MP4, MOV, AVI, MKV, WebM"
            )
        if uploaded_file.size > self.MAX_FILE_SIZE:
            raise serializers.ValidationError(
                "Il file supera la dimensione massima di 500MB"
            )

        temp_path = None  # file video temporaneo (solo InMemoryUploadedFile)
        thumbnail_temp_path = None  # thumbnail JPEG estratto

        try:
            # ----- File già su disco (TemporaryUploadedFile) -----
            if isinstance(uploaded_file, TemporaryUploadedFile):
                uploaded_file.seek(0)
                logger.info(
                    "[video_serializer] TemporaryUploadedFile "
                    "rilevato, estraggo durata..."
                )

                with VideoFileClip(uploaded_file.temporary_file_path()) as clip:
                    validated_data["duration"] = int(clip.duration)
                    thumbnail_temp_path = self._extract_thumbnail(clip)

            # ----- File in memoria (InMemoryUploadedFile) -----
            elif isinstance(uploaded_file, InMemoryUploadedFile):
                uploaded_file.seek(0)
                logger.info(
                    "[video_serializer] InMemoryUploadedFile "
                    "rilevato, salvo su disco temporaneo..."
                )

                # Genera un path temporaneo chiuso
                temp_path = (
                    Path(tempfile.gettempdir())
                    / f"{uuid.uuid4()}{Path(uploaded_file.name).suffix}"
                )

                # Copia i chunk nel file
                with open(temp_path, "wb") as tmp:
                    for chunk in uploaded_file.chunks():
                        tmp.write(chunk)

                logger.info(f"[video_serializer] File temporaneo creato: {temp_path}")

                # Ora che il file è chiuso, MoviePy può leggerlo
                with VideoFileClip(str(temp_path)) as clip:
                    validated_data["duration"] = int(clip.duration)
                    thumbnail_temp_path = self._extract_thumbnail(clip)

            # ----- Tipo non gestito -----
            else:
                logger.error(
                    f"[video_serializer] Tipo file non gestito: {type(uploaded_file)}"
                )
                raise serializers.ValidationError({"file": "File non valido."})

            logger.info(
                "[video_serializer] Duration extracted %s s, "
                "proceeding to save model...",
                validated_data["duration"],
            )

        except serializers.ValidationError:
            raise
        except Exception as e:
            logger.error(
                f"[video_serializer] Errore durante l'analisi del video: {str(e)}"
            )
            raise serializers.ValidationError(
                "Impossibile leggere i metadati del video. "
                "Verifica che il file non sia corrotto"
            )

        finally:
            # Pulizia del file temporaneo video, se creato
            if temp_path and Path(temp_path).exists():
                try:
                    Path(temp_path).unlink()
                    logger.info(
                        f"[video_serializer] File temporaneo cancellato: {temp_path}"
                    )
                except Exception as ex:
                    logger.warning(
                        "[video_serializer] Impossibile "
                        "cancellare file temporaneo %s: %s",
                        temp_path,
                        ex,
                    )

        # ----- Validazione durata (10s – 60s) -----
        duration = validated_data.get("duration", 0)
        if duration < 10 or duration > 60:
            self._cleanup_thumbnail_temp(thumbnail_temp_path)
            raise serializers.ValidationError(
                "La durata del video deve essere tra 10 secondi e 1 minuto"
            )

        # ----- Salvataggio del modello -----
        instance = super().create(validated_data)
        logger.info(
            f"[video_serializer] Video creato: {instance.title} (ID: {instance.id})"
        )
        logger.info(f"[video_serializer] File caricato: {instance.file.name}")
        logger.info(
            f"[video_serializer] File URL: {getattr(instance.file, 'url', 'NO URL')}"
        )

        # ----- Allegare thumbnail (graceful — non blocca l'upload) -----
        if thumbnail_temp_path and Path(thumbnail_temp_path).exists():
            try:
                thumb_name = f"thumbnails/{uuid.uuid4().hex}.jpg"
                with open(thumbnail_temp_path, "rb") as f:
                    instance.thumbnail.save(thumb_name, DjangoFile(f), save=True)
                logger.info("[video_serializer] Thumbnail salvato: %s", thumb_name)
            except Exception as e:
                logger.warning(
                    "[video_serializer] Impossibile salvare thumbnail: %s", e
                )
            finally:
                self._cleanup_thumbnail_temp(thumbnail_temp_path)

        return instance

    @staticmethod
    def _extract_thumbnail(clip):
        """Estrae un frame dal video come thumbnail JPEG. Ritorna path o None."""
        try:
            thumb_path = Path(tempfile.gettempdir()) / f"thumb_{uuid.uuid4().hex}.jpg"
            clip.save_frame(str(thumb_path), t=min(1.0, clip.duration / 2))
            logger.info("[video_serializer] Thumbnail estratto: %s", thumb_path)
            return str(thumb_path)
        except Exception as e:
            logger.warning("[video_serializer] Impossibile estrarre thumbnail: %s", e)
            return None

    @staticmethod
    def _cleanup_thumbnail_temp(thumbnail_temp_path):
        """Rimuove il file thumbnail temporaneo, se esiste."""
        if thumbnail_temp_path:
            try:
                Path(thumbnail_temp_path).unlink(missing_ok=True)
            except Exception:
                pass


class VideoUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ("title", "tag", "allow_download")
        extra_kwargs = {"title": {"required": True}, "tag": {"required": True}}

    def update(self, instance, validated_data):
        logger.info(f"[video_serializer] Aggiornamento video ID {instance.id}")
        if "tag" in validated_data and validated_data["tag"] != instance.tag:
            logger.info(
                "[video_serializer] Cambio contest per video ID %s (tag: %s)",
                instance.id,
                validated_data["tag"],
            )
            nuovo_contest = get_or_create_current_contest(validated_data["tag"])
            validated_data["contest"] = nuovo_contest
        return super().update(instance, validated_data)

    # TODO una volta che il video ha vinto il contest, non può più essere cancellato
