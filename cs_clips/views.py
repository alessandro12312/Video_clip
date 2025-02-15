# Controllers for the API endpoints
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model
from django.db import models
from .models import Video, Rating, Comment
from .serializers import (
    ErrorResponseSerializer, UserSerializer, VideoSerializer,
    UserRegistrationSerializer, RatingSerializer, CommentSerializer
)
from rest_framework.decorators import action
from rest_framework.response import Response

User = get_user_model()

# Common error handling mixin
def handle_exception_with_serializer(exc):
    error_serializer = ErrorResponseSerializer({
        'errors': [
            {
                'type': exc.__class__.__name__,  # Nome dell'eccezione
                'message': str(exc)              # Messaggio di errore
            }
        ]
    })
    return Response(error_serializer.data, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        return [AllowAny()] if self.action == 'create' else super().get_permissions()

    def get_serializer_class(self):
        return UserRegistrationSerializer if self.action == 'create' else UserSerializer

    def handle_exception(self, exc):
        return handle_exception_with_serializer(exc)

class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(uploader=self.request.user)

    @action(detail=False, methods=['get'], url_path='top-rated')
    def top_rated(self, request):
        videos = Video.objects.annotate(average_rating=models.Avg('ratings__value')).order_by('-average_rating')
        page = self.paginate_queryset(videos)
        serializer = self.get_serializer(page or videos, many=True)
        return self.get_paginated_response(serializer.data) if page else Response(serializer.data)

    def handle_exception(self, exc):
        return handle_exception_with_serializer(exc)

class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def handle_exception(self, exc):
        return handle_exception_with_serializer(exc)

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def handle_exception(self, exc):
        return handle_exception_with_serializer(exc)
