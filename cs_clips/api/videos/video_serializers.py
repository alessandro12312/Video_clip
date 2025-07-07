# Video serializer
from functools import lru_cache
from pathlib import Path
from django.core.files.uploadedfile import TemporaryUploadedFile, InMemoryUploadedFile
from moviepy import VideoFileClip
from rest_framework import serializers
from cs_clips.models import Video
from cs_clips.utils.get_date_util import get_or_create_current_contest
from drf_spectacular.utils import extend_schema_field
from minio import Minio, S3Error
import os, tempfile, uuid
from datetime import timedelta
import logging

from project_clip import settings

logger = logging.getLogger('django')

class VideoOutputSerializer(serializers.ModelSerializer):
    uploader = serializers.ReadOnlyField(source='uploader.username')
    average_rating = serializers.SerializerMethodField()
    file = serializers.FileField(read_only=True, help_text="URL del file video.")
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = (
            'id', 'title', 'duration', 'file', 'file_url', 'uploader',
            'average_rating', 'created_at', 'updated_at', 'contest', 'tag'
        )
        read_only_fields = (
            'created_at', 'updated_at', 'uploader', 'contest', 'views', 'average_rating', 'file', 'file_url'
        )

    @extend_schema_field(serializers.FloatField)
    def get_average_rating(self, obj):
        ratings = obj.ratings.all()
        if not ratings.exists():
            return 0.0
        return round(sum(r.value for r in ratings) / ratings.count(), 2)
    
    @staticmethod
    @lru_cache(maxsize=1)                             # evita di ricreare il client ad ogni chiamata
    def _get_minio_client() -> Minio:
        """
        Restituisce un singleton di Minio client inizializzato
        con i parametri definiti in settings.py.
        """
        return Minio(
            endpoint   = settings.MINIO_STORAGE_ENDPOINT,
            access_key = settings.MINIO_STORAGE_ACCESS_KEY,
            secret_key = settings.MINIO_STORAGE_SECRET_KEY,
            secure     = settings.MINIO_STORAGE_USE_HTTPS,
        )

    def get_file_url(self, obj):
        """
        Genera una presigned-URL valida **1 ora** dal bucket MinIO
        indicato in settings.  
        Se MinIO non risponde restituisce l'URL locale,
        così evitiamo un 500 e diamo comunque un link al client.
        """
        if not obj.file:
            return None

        bucket_name  = settings.MINIO_STORAGE_MEDIA_BUCKET_NAME
        object_name  = obj.file.name
        client       = self._get_minio_client()
        return client.presigned_get_object(bucket_name, object_name,
                                                expires=timedelta(hours=1))
        

class VideoInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ('title', 'file', 'tag')


    #TODO rivedi come genera il contest
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
        logger.info(f"Tipo file ricevuto: {type(uploaded_file)}")

        if not uploaded_file:
            logger.error("File non fornito.")
            raise serializers.ValidationError({"file": "File non fornito."})

        temp_path = None  # servirà per la pulizia finale

        try:
            # ----- File già su disco (TemporaryUploadedFile) -----
            if isinstance(uploaded_file, TemporaryUploadedFile):
                uploaded_file.seek(0)
                with VideoFileClip(uploaded_file.temporary_file_path()) as clip:
                    validated_data["duration"] = int(clip.duration)

            # ----- File in memoria (InMemoryUploadedFile) -----
            elif isinstance(uploaded_file, InMemoryUploadedFile):
                uploaded_file.seek(0)

                # 1. Genera un path temporaneo chiuso
                temp_path = (
                    Path(tempfile.gettempdir())
                    / f"{uuid.uuid4()}{Path(uploaded_file.name).suffix}"
                )

                # 2. Copia i chunk nel file
                with open(temp_path, "wb") as tmp:
                    for chunk in uploaded_file.chunks():
                        tmp.write(chunk)

                # 3. Ora che il file è chiuso, MoviePy può leggerlo
                with VideoFileClip(str(temp_path)) as clip:
                    validated_data["duration"] = int(clip.duration)

            # ----- Tipo non gestito -----
            else:
                logger.error(f"Tipo file non gestito: {type(uploaded_file)}")
                raise serializers.ValidationError({"file": "File non valido."})

            logger.info(
                f"Duration extracted {validated_data['duration']} s, proceeding to save model..."
            )

        except Exception as e:
            logger.error(f"Errore durante l'analisi del video: {str(e)}")
            raise serializers.ValidationError(
                {"file": f"Impossibile analizzare il video: {str(e)}"}
            )

        finally:
            # Pulizia del file temporaneo, se creato
            if temp_path and Path(temp_path).exists():
                try:
                    Path(temp_path).unlink()
                except Exception as ex:
                    logger.warning(
                        f"Impossibile cancellare file temporaneo {temp_path}: {ex}"
                    )

        # ----- Salvataggio del modello -----
        instance = super().create(validated_data)
        logger.info(f"Video creato: {instance.title} (ID: {instance.id})")
        logger.info(f"File caricato: {instance.file.name}")
        logger.info(f"File URL: {getattr(instance.file, 'url', 'NO URL')}")

        return instance

class VideoUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ('title', 'tag')
        extra_kwargs = {
            'title': {'required': True},
            'tag': {'required': True}
        }

    def update(self, instance, validated_data):
        if 'tag' in validated_data and validated_data['tag'] != instance.tag:
            nuovo_contest = get_or_create_current_contest(validated_data['tag'])
            validated_data['contest'] = nuovo_contest
        return super().update(instance, validated_data)

    
    #TODO una volta che il video ha vinto il contest, non può più essere cancellato