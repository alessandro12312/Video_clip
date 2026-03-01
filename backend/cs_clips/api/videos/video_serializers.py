# Video serializer
import logging
import tempfile
import uuid
from datetime import timedelta
from functools import lru_cache
from pathlib import Path

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

    class Meta:
        model = Video
        fields = (
            "id",
            "title",
            "duration",
            "file",
            "file_url",
            "uploader",
            "average_rating",
            "created_at",
            "updated_at",
            "contest",
            "tag",
        )
        read_only_fields = (
            "created_at",
            "updated_at",
            "uploader",
            "contest",
            "views",
            "average_rating",
            "file",
            "file_url",
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
    class Meta:
        model = Video
        fields = ("title", "file", "tag")

    # TODO rivedi come genera il contest
    def create(self, validated_data):
        """
        Crea un Video:
        1. Salva l'oggetto in DB (senza durata).
        2. Scrive il file uploadato in un temp locale *chiuso* (no lock).
        3. Usa MoviePy/Ffmpeg per estrarne la durata.
        4. Aggiorna e salva di nuovo il Video con la durata.
        5. Cancella il file temporaneo.
        """
        uploaded_file = validated_data.get("file")
        logger.info(f"[video_serializer] Tipo file ricevuto: {type(uploaded_file)}")

        if not uploaded_file:
            logger.error("[video_serializer] File non fornito.")
            raise serializers.ValidationError({"file": "File non fornito."})

        temp_path = None  # servirà per la pulizia finale

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

        except Exception as e:
            logger.error(
                f"[video_serializer] Errore durante l'analisi del video: {str(e)}"
            )
            raise serializers.ValidationError(
                {"file": f"Impossibile analizzare il video: {str(e)}"}
            )

        finally:
            # Pulizia del file temporaneo, se creato
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

        # ----- Salvataggio del modello -----
        instance = super().create(validated_data)
        logger.info(
            f"[video_serializer] Video creato: {instance.title} (ID: {instance.id})"
        )
        logger.info(f"[video_serializer] File caricato: {instance.file.name}")
        logger.info(
            f"[video_serializer] File URL: {getattr(instance.file, 'url', 'NO URL')}"
        )

        return instance


class VideoUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ("title", "tag")
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
