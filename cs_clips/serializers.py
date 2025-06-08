# DTOs for the API
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Video, Rating, Comment
from django.contrib.auth import get_user_model

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


class VideoSerializer(serializers.ModelSerializer):
    uploader = serializers.ReadOnlyField(source='uploader.username')
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = ('id', 'title', 'file', 'uploader', 
                 'average_rating', 'views', 'created_at', 'updated_at','tags')
        read_only_fields = ('created_at', 'updated_at')


    def get_average_rating(self, obj):
        ratings = obj.ratings.all()
        if not ratings:
            return None
        return sum(r.value for r in ratings) / len(ratings)


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
        fields = ('id', 'user', 'video', 'content', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')


# Error response serializer
class ErrorResponseSerializer(serializers.Serializer):
    code = serializers.CharField(help_text="Codice di errore", required=False)
    detail = serializers.CharField(help_text="Descrizione dell'errore")
    