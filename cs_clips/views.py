# Controllers for the API endpoints
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from cs_clips.permissions import RoleBasedPermission
from rest_framework.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Avg
from .models import Video, Rating, Comment, Contest
from .serializers import (
    ErrorResponseSerializer, UserSerializer, VideoSerializer,
    UserRegistrationSerializer, RatingSerializer, CommentSerializer
)
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import Group
from rest_framework.views import APIView
from .utils.getDateUtil import get_or_create_current_contest
from django.utils import timezone


User = get_user_model()


# Common error handling mixin
def handle_exception_with_serializer(exc):
    if isinstance(exc, ValidationError):
        if isinstance(exc.detail, dict):
            # Prende il primo errore per chiarezza
            field, errors = next(iter(exc.detail.items()))
            detail_message = f"Campo mancante: '{field}' - {', '.join([str(e) for e in errors])}"
        elif isinstance(exc.detail, list):
            # Per errori non legati a campi specifici
            detail_message = '; '.join([str(error) for error in exc.detail])
        else:
            detail_message = str(exc)
        code = "ValidationError"
    else:
        detail_message = str(exc)
        code = exc.__class__.__name__

    error_serializer = ErrorResponseSerializer({
        'code': code,
        'detail': detail_message
    })
    return Response(error_serializer.data, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, RoleBasedPermission]

    def get_permissions(self):
        return [AllowAny()] if self.action == 'create' else super().get_permissions()

    def get_serializer_class(self):
        return UserRegistrationSerializer if self.action == 'create' else UserSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        # Assegna automaticamente l'utente al gruppo 'toconfirm'
        group, created = Group.objects.get_or_create(name='toconfirm')
        user.groups.add(group)

    def handle_exception(self, exc):
        return handle_exception_with_serializer(exc)
    

class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes = [IsAuthenticated, RoleBasedPermission]

    def perform_create(self, serializer):
        contest = get_or_create_current_contest()
        serializer.save(uploader=self.request.user, contest=contest)

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
    permission_classes = [IsAuthenticated, RoleBasedPermission]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def handle_exception(self, exc):
        return handle_exception_with_serializer(exc)

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, RoleBasedPermission]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def handle_exception(self, exc):
        return handle_exception_with_serializer(exc)
    

class EndContestView(APIView):
    """
    Endpoint per chiudere il contest attivo e decretare il vincitore.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        today = timezone.now().date()
        contest = Contest.objects.filter(
            start_date__lte=today,
            end_date__gte=today,
            is_closed=False
        ).first()
        if not contest:
            return Response({"detail": "Nessun contest attivo da chiudere."}, status=status.HTTP_404_NOT_FOUND)

        # Trova il video vincitore (media voto più alta)
        video = (
            Video.objects
            .filter(contest=contest)
            .annotate(avg_rating=Avg('ratings__value'))
            .order_by('-avg_rating', '-created_at')
            .first()
        )
        contest.is_closed = True
        closed_at_now = contest.closed_at = timezone.now()
        contest.save()

        winner_data = VideoSerializer(video).data if video else None

        return Response({
            "contest": {
                "id": contest.id,
                "name": contest.name,
                "start_date": contest.start_date,
                "end_date": closed_at_now,
            },
            "winner": winner_data
        }, status=status.HTTP_200_OK)


class ContestWinnersView(APIView):
    """
    Endpoint che restituisce una lista dei video vincitori
    dei contest passati (chiusi).
    Il vincitore è il video con la media voto più alta.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        winners = []
        # Prendi solo contest passati (finito prima di oggi)
        contests = Contest.objects.filter(end_date__lt=timezone.now().date())
        for contest in contests:
            # Trova i video di questo contest e calcola la media voto
            video = (
                Video.objects
                .filter(contest=contest)
                .annotate(avg_rating=Avg('ratings__value'))
                .order_by('-avg_rating', '-created_at')  # in caso di pari merito prende il più recente
                .first()
            )
            if video:
                winners.append(video)
        # Serializza la lista dei vincitori
        data = VideoSerializer(winners, many=True).data
        return Response(data)