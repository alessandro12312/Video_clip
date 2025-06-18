# Video serializer
from moviepy import VideoFileClip
from rest_framework import serializers
from cs_clips.models import Video
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
            """
            Override del metodo create per impostare automaticamente la durata del video.
            Prima salva il modello,
            poi calcola la durata e aggiorna il campo duration.
            """
            # Salva il modello
            instance = super().create(validated_data)

            # Calcola la durata usando il path reale del file già salvato
            try:
                absolute_path = instance.file.path  # Path del file in /media/videos/...
                with VideoFileClip(absolute_path) as clip:
                    instance.duration = int(clip.duration)
                    instance.save(update_fields=["duration"])
            except Exception as e:
                # In caso di errore, elimina il record per non lasciare dati inconsistenti
                instance.delete()
                raise serializers.ValidationError({'file': f"Impossibile calcolare la durata del video: {str(e)}"})
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

    