from rest_framework import serializers
from django.contrib.auth.models import User
from .models import VideoUpload

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class VideoUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoUpload
        fields = ['id', 'user', 'title', 'video', 'uploaded_at']
        read_only_fields = ['user', 'uploaded_at']