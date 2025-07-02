# Video serializer
import os
import tempfile
from moviepy import VideoFileClip
from rest_framework import serializers
from cs_clips.models import Video
from cs_clips.utils.calculate_video_duration_util import calculate_video_duration_task 
from cs_clips.utils.get_date_util import get_or_create_current_contest

class VideoSerializer(serializers.ModelSerializer):
    uploader = serializers.ReadOnlyField(source='uploader.username')
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = ('id', 'title', 'file', 'uploader', 
                 'average_rating', 'created_at', 'updated_at', 'contest', 'tag')
        read_only_fields = ('created_at', 'updated_at', 'uploader', 'contest', 'views', 'average_rating')
        extra_kwargs = {
            'title': {'required': True},
            'tag': {'required': True}
        }

    def get_average_rating(self, obj):
        """
        Calcola la media dei voti, escludendo i video senza voti.
        Ritorna 0.0 invece di None se non ci sono voti.
        """
        ratings = obj.ratings.all()
        if not ratings.exists():
            return 0.0
        return round(sum(r.value for r in ratings) / ratings.count(), 2)
    
    def create(self, validated_data):
        uploaded_file = validated_data.get('file')
        if not uploaded_file:
            raise serializers.ValidationError({'file': 'File non fornito.'})

        tmp_file_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp:
                for chunk in uploaded_file.chunks():
                    tmp.write(chunk)
                tmp_file_path = tmp.name
            with VideoFileClip(tmp_file_path) as clip:
                validated_data['duration'] = int(clip.duration)
        except Exception as e:
            raise serializers.ValidationError({'file': f"Impossibile analizzare il video: {str(e)}"})
        finally:
            if tmp_file_path and os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)

        instance = super().create(validated_data)
        print(f"DEBUG: URL del file dopo il salvataggio: {instance.file.url}")
        print(f"DEBUG: Nome del file dopo il salvataggio: {instance.file.name}")
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

    