from datetime import timedelta
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db.models import Avg, F
from cs_clips.permissions import RoleBasedPermission
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from cs_clips.exceptions.error_handler import handle_exception_with_serializer
from cs_clips.models import Video
from cs_clips.api.videos.video_serializers import VideoSerializer, VideoUpdateSerializer
from cs_clips.utils.get_date_util import get_or_create_current_contest



@extend_schema(
        parameters=[
            OpenApiParameter(name='page', type=int, required=False, description='Numero della pagina'),
            OpenApiParameter(name='page_size', type=int, required=False, description='Numero di risultati per pagina')
        ]
    )
class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all().order_by('-created_at')  # Ordina dal più recente al meno recente
    serializer_class = VideoSerializer  # Default serializer per GET e POST
    permission_classes = [IsAuthenticated, RoleBasedPermission]

    def perform_create(self, serializer):
        """
        Salva il video e lo associa al contest corrente.
        L'upload fisico del file viene gestito automaticamente dal backend di storage
        (es. MinIO S3), tramite il campo FileField e il serializer.
        """
        tag = self.request.data.get('tag')
        if not tag:
            raise ValidationError({"tag": "Questo campo è obbligatorio."})
        contest = get_or_create_current_contest(tag)
        serializer.save(uploader=self.request.user, contest=contest, tag=tag)

    def update(self, request, *args, **kwargs):
        """
        PUT → input con VideoUpdateSerializer, output con VideoSerializer
        """
        instance = self.get_object()
        serializer = VideoUpdateSerializer(instance, data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(VideoSerializer(instance, context={'request': request}).data, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        """
        PATCH → input con VideoUpdateSerializer, output con VideoSerializer
        """
        instance = self.get_object()
        serializer = VideoUpdateSerializer(instance, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(VideoSerializer(instance, context={'request': request}).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='following')
    def videos_from_following(self, request):
        """
        Restituisce i video caricati dagli utenti che l'utente autenticato segue.
        Ordinati dal più recente al meno recente.
        """
        user = request.user

        
        # Controllo permessi: solo user e superuser SOLO PER TEST
        # if not user.is_authenticated or (
        #     not user.is_superuser and not user.groups.filter(name='user').exists()
        # ):
        #     return Response({'detail': 'Accesso negato. Solo per utenti confermati.'},
        #                     status=status.HTTP_403_FORBIDDEN)


        following_users = user.following.all()

        # Filtra i video caricati dagli utenti seguiti
        videos = Video.objects.filter(uploader__in=following_users).order_by('-created_at')

        # Applica paginazione globale
        page = self.paginate_queryset(videos)
        serializer = self.get_serializer(page or videos, many=True)

        return self.get_paginated_response(serializer.data) if page else Response(serializer.data)

    # Documentazione OpenAPI per l'endpoint top_rated
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='range',
                description='Intervallo temporale: day, week, month, year, all',
                required=False,
                type=str,
                enum=['day', 'week', 'month', 'year', 'all']
            )
        ]
    )
    # Top rated in base a un intervallo di tempo controllo da FE per spaziare automaticamente quando finiscono i video
    @action(detail=False, methods=['get'], url_path='top-rated')
    def top_rated(self, request):
        """
        Restituisce i video top-rated filtrabili per intervallo temporale:
        day, week, month, year, all (default: all).
        """
        range_param = request.query_params.get('range', 'all')
        now = timezone.now()

        # Calcola l'intervallo di tempo
        time_ranges = {
            'day': now - timedelta(days=1),
            'week': now - timedelta(days=7),
            'month': now - timedelta(days=30),
            'year': now - timedelta(days=365),
            'all': None
        }

        # Valida parametro
        if range_param not in time_ranges:
            return Response({"detail": f"Intervallo non valido: {range_param}"}, status=400)

        queryset = Video.objects.all()
        if time_ranges[range_param]:
            queryset = queryset.filter(created_at__gte=time_ranges[range_param])

        # Calcolo della media voto
        queryset = queryset.annotate(average_rating=Avg('ratings__value')).order_by('-average_rating')

        # Paginazione
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page or queryset, many=True)
        return self.get_paginated_response(serializer.data) if page else Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='views', parser_classes=[])
    def views(self, request, pk=None):
        """
        Endpoint per incrementare le visualizzazioni di un video.
        Deve essere chiamato dal frontend ogni volta che il video viene effettivamente visualizzato.
        5/10 secondi controllo da frontend
        """
        video = self.get_object()
        video.views = F('views') + 1
        video.save(update_fields=['views'])
        video.refresh_from_db()  # aggiorna il valore da DB
        return Response({'views': video.views}, status=status.HTTP_200_OK)

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return VideoUpdateSerializer
        return VideoSerializer

    def handle_exception(self, exc):
        return handle_exception_with_serializer(exc)
    