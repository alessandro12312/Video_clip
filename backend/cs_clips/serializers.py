# DTOs for the API
import os
from moviepy import VideoFileClip
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import Contest, Video, Rating, Comment, VideoLike, CommentLike, Notification
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password as django_validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.files.storage import default_storage
from django.db import transaction

# Costanti di validazione upload video
ALLOWED_VIDEO_EXTENSIONS = {'.mp4', '.mov', '.avi', '.mkv', '.webm'}
MAX_VIDEO_FILE_SIZE = 500 * 1024 * 1024  # 500MB
MIN_VIDEO_DURATION = 10   # secondi
MAX_VIDEO_DURATION = 60   # secondi

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    is_followed_by_me = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'bio', 'created_at', 'updated_at',
                  'followers', 'following', 'followers_count', 'following_count',
                  'is_followed_by_me')
        read_only_fields = ('created_at', 'updated_at')

    def get_followers_count(self, obj):
        """Restituisce il numero di follower (usa annotazione se disponibile)."""
        return getattr(obj, 'annotated_followers_count', obj.followers.count())

    def get_following_count(self, obj):
        """Restituisce il numero di utenti seguiti (usa annotazione se disponibile)."""
        return getattr(obj, 'annotated_following_count', obj.following.count())

    def get_is_followed_by_me(self, obj):
        """Restituisce True se l'utente autenticato segue questo utente."""
        request = self.context.get('request')
        if not request or not request.user or not request.user.is_authenticated:
            return False
        if not hasattr(self, '_following_ids'):
            self._following_ids = set(request.user.following.values_list('id', flat=True))
        return obj.id in self._following_ids

    def to_representation(self, instance):
        """Nasconde l'email per utenti non proprietari del profilo."""
        data = super().to_representation(instance)
        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated:
            if request.user.id != instance.id:
                data.pop('email', None)
        else:
            data.pop('email', None)
        return data


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer per la modifica del profilo utente (solo campi consentiti)."""

    class Meta:
        model = User
        fields = ('bio',)

    def validate_bio(self, value):
        if len(value) > 500:
            raise serializers.ValidationError("La bio non può superare i 500 caratteri.")
        return value


class UserRegistrationSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=150,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message="Username già in uso.",
                lookup='iexact'
            )
        ]
    )
    email = serializers.EmailField(
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message="Email già registrata.",
                lookup='iexact'
            )
        ]
    )
    password = serializers.CharField(
        write_only=True,
        help_text="Minimo 8 caratteri, non interamente numerica, non troppo comune"
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def validate(self, data):
        # Crea un oggetto user temporaneo per UserAttributeSimilarityValidator
        temp_user = User(username=data.get('username', ''), email=data.get('email', ''))
        try:
            django_validate_password(data['password'], user=temp_user)
        except DjangoValidationError as e:
            raise serializers.ValidationError({'password': e.messages})
        return data

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
    like_count = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = ('id', 'title', 'file', 'uploader',
                 'average_rating', 'like_count', 'views', 'duration',
                 'allow_download', 'created_at', 'updated_at', 'contest', 'tag')
        read_only_fields = ('created_at', 'updated_at', 'uploader', 'contest')
        extra_kwargs = {'tag': {'required': True}}


    def get_average_rating(self, obj):
        """
        Calcola la media dei voti, escludendo i video senza voti.
        Ritorna 0.0 invece di None se non ci sono voti.
        """
        ratings = obj.ratings.all()
        if not ratings.exists():
            return 0.0
        return round(sum(r.value for r in ratings) / ratings.count(), 2)

    def get_like_count(self, obj):
        """Restituisce il numero di like del video."""
        return getattr(obj, 'annotated_like_count', obj.likes.count())

    def validate_file(self, value):
        """Validazione pre-save: dimensione, estensione e content-type."""
        # Controllo dimensione
        if value.size > MAX_VIDEO_FILE_SIZE:
            raise serializers.ValidationError("Il file supera la dimensione massima di 500MB")
        # Controllo estensione
        ext = os.path.splitext(value.name)[1].lower()
        if ext not in ALLOWED_VIDEO_EXTENSIONS:
            raise serializers.ValidationError(
                "Formato non supportato. Formati accettati: MP4, MOV, AVI, MKV, WebM"
            )
        # Controllo content-type
        if not value.content_type.startswith('video/'):
            raise serializers.ValidationError("Il file selezionato non è un video")
        return value

    def create(self, validated_data):
        """
        Override del metodo create per impostare automaticamente la durata del video.
        Wrappato in transaction.atomic() per rollback sicuro se la validazione durata fallisce.
        """
        with transaction.atomic():
            instance = super().create(validated_data)

            try:
                absolute_path = instance.file.path
                with VideoFileClip(absolute_path) as clip:
                    duration = int(clip.duration)
            except Exception as e:
                try:
                    instance.delete()
                except Exception:
                    pass
                raise serializers.ValidationError(
                    {'file': [f"Impossibile calcolare la durata del video: {str(e)}"]}
                )

            if duration < MIN_VIDEO_DURATION or duration > MAX_VIDEO_DURATION:
                try:
                    instance.delete()
                except Exception:
                    pass
                raise serializers.ValidationError(
                    {'file': ["Il video deve durare tra 10 secondi e 1 minuto"]}
                )

            instance.duration = duration
            instance.save(update_fields=["duration"])

        return instance


class RatingSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Rating
        fields = ('id', 'user', 'video', 'value', 'created_at', 'updated_at')
        read_only_fields = ('timestamp', 'created_at', 'updated_at')


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    like_count = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('id', 'user', 'video', 'content', 'timestamp_second',
                 'is_disabled', 'like_count', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at', 'is_disabled')

    def get_like_count(self, obj):
        """Restituisce il numero di like del commento."""
        return getattr(obj, 'annotated_like_count', obj.likes.count())

    def validate(self, data):
        """
        Valida che timestamp_second sia >= 0 e non superi la durata del video.
        """
        timestamp = data.get('timestamp_second')
        video = data.get('video')
        if timestamp < 0:
            raise serializers.ValidationError({
                "timestamp_second": "Il valore deve essere maggiore o uguale a 0."
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


class PopupCommentSerializer(serializers.Serializer):
    timestamp = serializers.IntegerField(help_text="Secondo del video")
    comment_id = serializers.IntegerField(help_text="ID del commento")
    text = serializers.CharField(help_text="Testo del commento")
    author = serializers.CharField(help_text="Username dell'autore")
    like_count = serializers.IntegerField(help_text="Numero di like")


# Error response serializer
class ErrorResponseSerializer(serializers.Serializer):
    code = serializers.CharField(help_text="Codice di errore", required=False)
    detail = serializers.CharField(help_text="Descrizione dell'errore")
    