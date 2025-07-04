# Video serializer
from django.core.files.uploadedfile import TemporaryUploadedFile, InMemoryUploadedFile
from moviepy import VideoFileClip
from rest_framework import serializers
from cs_clips.models import Video
from cs_clips.utils.get_date_util import get_or_create_current_contest
from drf_spectacular.utils import extend_schema_field
from minio import Minio
import os
from datetime import timedelta
import logging

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

    def get_file_url(self, obj):
        if obj.file:
            minio_client = Minio(
                endpoint=os.getenv("MINIO_STORAGE_ENDPOINT", "localhost:9000"),
                access_key=os.getenv("MINIO_STORAGE_ACCESS_KEY", "console"),
                secret_key=os.getenv("MINIO_STORAGE_SECRET_KEY", "console_access_key"),
                secure=os.getenv("MINIO_STORAGE_USE_HTTPS", "False").lower() == "true",
            )
            bucket_name = os.getenv("MINIO_STORAGE_MEDIA_BUCKET_NAME", "clips")
            object_name = obj.file.name
            # Presigned URL valido per 1 ora
            url = minio_client.presigned_get_object(
                bucket_name, object_name, expires=timedelta(hours=1)
            )
            return url
        return None

class VideoInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ('title', 'file', 'tag')

    def create(self, validated_data):
        uploaded_file = validated_data.get('file')
        if not uploaded_file:
            logger.error("File non fornito.")
            raise serializers.ValidationError({'file': 'File non fornito.'})
        try:
            if isinstance(uploaded_file, TemporaryUploadedFile):
                uploaded_file.seek(0)
                with VideoFileClip(uploaded_file.temporary_file_path()) as clip:
                    validated_data['duration'] = int(clip.duration)
            else:
                raise serializers.ValidationError({'file': 'File non valido.'})
            logger.info(f"Duration extracted {int(clip.duration)}, proceeding to save model...")
        except Exception as e:
            logger.error(f"Errore durante l'analisi del video: {str(e)}")
            raise serializers.ValidationError({'file': f"Impossibile analizzare il video: {str(e)}"})

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