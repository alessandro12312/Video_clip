# Controllers for the API endpoints
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model
from .models import Video, Rating, Comment
from django.db import models
from .serializers import UserSerializer, VideoSerializer, UserRegistrationSerializer, RatingSerializer, CommentSerializer
from rest_framework.decorators import action
from rest_framework.response import Response

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegistrationSerializer
        return UserSerializer


class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(uploader=self.request.user)
    
    @action(detail=False, methods=['get'], url_path='top-rated')
    def top_rated(self, request):
        """
        Restituisce una lista di video ordinati per rating, dal più alto al più basso.
        """
        # Ordiniamo i video in base alla media dei rating (dal più alto al più basso)
        videos = Video.objects.annotate(
            average_rating=models.Avg('ratings__value')  # Calcoliamo la media dei rating
        ).order_by('-average_rating')  # Ordiniamo dal più alto al più basso

        # Serializziamo i video
        page = self.paginate_queryset(videos)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(videos, many=True)
        return Response(serializer.data)


class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)