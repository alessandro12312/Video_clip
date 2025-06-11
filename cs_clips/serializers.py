# DTOs for the API
from moviepy import VideoFileClip
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Contest, Video, Rating, Comment
from django.contrib.auth import get_user_model
from django.core.files.storage import default_storage




User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user


class ContestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contest
        fields = ('id', 'name', 'tag', 'start_date', 'end_date', 'is_closed', 'closed_at')
        extra_kwargs = {'tag': {'required': True}}


class VideoSerializer(serializers.ModelSerializer):
    uploader = serializers.ReadOnlyField(source='uploader.username')
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = ('id', 'title', 'file', 'uploader', 
                 'average_rating', 'views', 'created_at', 'updated_at', 'contest', 'tag')
        read_only_fields = ('created_at', 'updated_at', 'uploader', 'contest')
        extra_kwargs = {'tag': {'required': True}}

    def get_average_rating(self, obj):
        ratings = obj.ratings.all()
        if not ratings:
            return None
        return sum(r.value for r in ratings) / len(ratings)
    
    def create(self, validated_data):
            """
            Override del metodo create per impostare automaticamente la durata del video.
            """
            video_file = validated_data.get('file')
            # Salva temporaneamente il file se non è già su disco
            temp_path = default_storage.save(video_file.name, video_file)
            absolute_path = default_storage.path(temp_path)
            try:
                # Calcola la durata in secondi
                with VideoFileClip(absolute_path) as clip:
                    duration = int(clip.duration)  # Intero, in secondi
                validated_data['duration'] = duration
            except Exception as e:
                raise serializers.ValidationError({'file': f"Impossibile calcolare la durata del video: {str(e)}"})
            finally:
                # Cancella il file temporaneo solo se non usi default_storage con Media
                # os.remove(absolute_path) # Solo se necessario
                pass
            return super().create(validated_data)


class RatingSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Rating
        fields = ('id', 'user', 'video', 'value', 'created_at', 'updated_at')
        read_only_fields = ('timestamp', 'created_at', 'updated_at')


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Comment
        fields = ('id', 'user', 'video', 'content', 'timestamp_second', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')
    
    def validate(self, data):
        """
        Valida che timestamp_second sia >= 1 e non superi la durata del video.
        """
        timestamp = data.get('timestamp_second')
        video = data.get('video')
        if timestamp < 1:
            raise serializers.ValidationError({
                "timestamp_second": "Il valore deve essere maggiore o uguale a 1."
            })
        if not video or video.duration is None:
            raise serializers.ValidationError({
                "video": "Il video deve avere una durata impostata."
            })
        if timestamp > video.duration:
            raise serializers.ValidationError({
                "timestamp_second": f"Il valore non può superare la durata del video ({video.duration} secondi)."
            })
        return data


# Error response serializer
class ErrorResponseSerializer(serializers.Serializer):
    code = serializers.CharField(help_text="Codice di errore", required=False)
    detail = serializers.CharField(help_text="Descrizione dell'errore")
    