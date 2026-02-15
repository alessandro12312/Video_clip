# Controllers for the API endpoints
from datetime import timedelta
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from cs_clips.permissions import OnlyUsersPermission, RoleBasedPermission
from rest_framework.exceptions import ValidationError, NotAuthenticated, PermissionDenied, NotFound, APIException
from django.contrib.auth import get_user_model
from django.db import models, IntegrityError
from django.db.models import Avg
from .models import Video, Rating, Comment, Contest, VideoLike, CommentLike
from .serializers import (
    ErrorResponseSerializer, UserSerializer, UserProfileUpdateSerializer,
    VideoSerializer, UserRegistrationSerializer, RatingSerializer,
    CommentSerializer, PopupCommentSerializer
)
from django.db.models import Count
from rest_framework.filters import SearchFilter
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import Group
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from .utils.getDateUtil import get_or_create_current_contest
from .utils.desempate import desempate_ponderato
from django.utils import timezone
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from drf_spectacular.utils import extend_schema, OpenApiParameter


User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user

        # Aggiorna last_access
        user.last_login = timezone.now()
        user.save(update_fields=["last_login"])
        return data

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


# error handling
def handle_exception_with_serializer(exc):
    """
    Gestisce le eccezioni restituendo una risposta serializzata,
    mappando le eccezioni DRF sui codici di stato HTTP standard.
    """

    print(f"Tipo eccezione: {type(exc)} - Dettaglio: {exc}")

    # Default values
    code = exc.__class__.__name__
    detail_message = str(exc)
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR  # Default per errori generici

    # 400 Bad Request (errori di validazione input)
    if isinstance(exc, ValidationError):
        # Se l'errore riguarda un campo specifico
        if hasattr(exc, "detail") and isinstance(exc.detail, dict):
            field, errors = next(iter(exc.detail.items()))
            detail_message = f"Campo '{field}': {', '.join([str(e) for e in errors])}"
        # Se è una lista di errori
        elif hasattr(exc, "detail") and isinstance(exc.detail, list):
            detail_message = '; '.join([str(error) for error in exc.detail])
        status_code = status.HTTP_400_BAD_REQUEST
        code = "ValidationError"

    # 401 Unauthorized (token mancante/scaduto o non autenticato)
    elif isinstance(exc, NotAuthenticated):
        status_code = status.HTTP_401_UNAUTHORIZED
        code = "NotAuthenticated"

    # 403 Forbidden (permessi non sufficienti)
    elif isinstance(exc, PermissionDenied):
        status_code = status.HTTP_403_FORBIDDEN
        code = "PermissionDenied"

    # 404 Not Found
    elif isinstance(exc, NotFound) or isinstance(exc, Http404) or isinstance(exc, ObjectDoesNotExist):
        status_code = status.HTTP_404_NOT_FOUND
        code = "NotFound"

    # 409 Conflict
    elif isinstance(exc, IntegrityError) or getattr(exc, "status_code", None) == status.HTTP_409_CONFLICT:
        status_code = status.HTTP_409_CONFLICT
        code = "Conflict"

    # 500 Internal Server Error (altro errore generico)
    elif isinstance(exc, APIException):
        # Se APIException ma non gestita sopra, fallback su 500
        # Alcune APIException personalizzate possono avere .status_code
        status_code = getattr(exc, "status_code", status.HTTP_500_INTERNAL_SERVER_ERROR)
        code = getattr(exc, "default_code", code)
        detail_message = getattr(exc, "detail", detail_message)

    # Prepara la risposta strutturata
    error_serializer = ErrorResponseSerializer({
        'code': code,
        'detail': detail_message
    })

    return Response(error_serializer.data, status=status_code)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('username')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, RoleBasedPermission]
    filter_backends = [SearchFilter]
    search_fields = ['username']

    def get_queryset(self):
        return User.objects.annotate(
            annotated_followers_count=Count('followers', distinct=True),
            annotated_following_count=Count('following', distinct=True),
        ).order_by('username')

    def get_permissions(self):
        return [AllowAny()] if self.action == 'create' else super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegistrationSerializer
        if self.action in ('update', 'partial_update'):
            return UserProfileUpdateSerializer
        return UserSerializer

    def perform_update(self, serializer):
        """Solo il proprietario può modificare il proprio profilo."""
        if self.request.user.id != serializer.instance.id:
            raise PermissionDenied("Non puoi modificare il profilo di un altro utente.")
        serializer.save()

    def perform_create(self, serializer):
        user = serializer.save()
        # Assegna automaticamente l'utente al gruppo 'toconfirm' (read-only fino a promozione)
        group, _ = Group.objects.get_or_create(name='toconfirm')
        user.groups.add(group)

    @action(detail=True, methods=['post'], url_path='follow', permission_classes=[OnlyUsersPermission])
    def follow(self, request, pk=None):
        """
        Permette all'utente autenticato di seguire un altro utente.
        Restituisce is_followed e followers_count aggiornato.
        Idempotente: se già segui, restituisce 200 con stato attuale.
        """
        target_user = self.get_object()
        if request.user == target_user:
            raise ValidationError("Non puoi seguire te stesso.")

        already_following = request.user.following.filter(pk=target_user.pk).exists()
        request.user.following.add(target_user)
        followers_count = target_user.followers.count()

        if already_following:
            return Response({
                "detail": f"Stai già seguendo {target_user.username}.",
                "is_followed": True,
                "followers_count": followers_count,
            })

        return Response({
            "detail": f"Hai iniziato a seguire {target_user.username}.",
            "is_followed": True,
            "followers_count": followers_count,
        })
    
    @action(detail=True, methods=['post'], url_path='unfollow', permission_classes=[OnlyUsersPermission])
    def unfollow(self, request, pk=None):
        """
        Permette all'utente autenticato di smettere di seguire un altro utente.
        Restituisce is_followed e followers_count aggiornato.
        Idempotente: se non segui, restituisce 200 con stato attuale.
        """
        target_user = self.get_object()
        was_following = request.user.following.filter(pk=target_user.pk).exists()
        request.user.following.remove(target_user)
        followers_count = target_user.followers.count()

        if not was_following:
            return Response({
                "detail": f"Non stavi seguendo {target_user.username}.",
                "is_followed": False,
                "followers_count": followers_count,
            })

        return Response({
            "detail": f"Hai smesso di seguire {target_user.username}.",
            "is_followed": False,
            "followers_count": followers_count,
        })

    @action(detail=True, methods=['get'], url_path='followers')
    def get_followers(self, request, pk=None):
        """
        Restituisce la lista paginata degli utenti che seguono questo utente.
        Usa il queryset annotato per evitare N+1 su followers_count/following_count.
        """
        target_user = self.get_object()
        followers = self.get_queryset().filter(pk__in=target_user.followers.all())
        page = self.paginate_queryset(followers)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(followers, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='following')
    def get_following(self, request, pk=None):
        """
        Restituisce la lista paginata degli utenti che questo utente sta seguendo.
        Usa il queryset annotato per evitare N+1 su followers_count/following_count.
        """
        target_user = self.get_object()
        following = self.get_queryset().filter(pk__in=target_user.following.all())
        page = self.paginate_queryset(following)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(following, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='by-username/(?P<username>[^/.]+)')
    def by_username(self, request, username=None):
        """
        Restituisce il profilo di un utente cercato per username.
        """
        try:
            user = self.get_queryset().get(username=username)
        except User.DoesNotExist:
            raise NotFound(f"Utente '{username}' non trovato.")
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    def handle_exception(self, exc):
        return handle_exception_with_serializer(exc)
    

class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes = [IsAuthenticated, RoleBasedPermission]
    filterset_fields = ['allow_download']

    def get_queryset(self):
        return Video.objects.annotate(
            annotated_like_count=Count('likes', distinct=True)
        ).order_by('-created_at')

    def perform_create(self, serializer):
        tag = self.request.data.get('tag')
        if not tag:
            raise ValidationError({"tag": "Questo campo è obbligatorio."})
        contest = get_or_create_current_contest(tag)
        serializer.save(uploader=self.request.user, contest=contest, tag=tag)

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
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(videos, many=True)
        return Response(serializer.data)

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
        queryset = queryset.annotate(average_rating=models.Avg('ratings__value')).order_by('-average_rating')

        # Paginazione
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='views')
    def views(self, request, pk=None):
        """
        Endpoint per incrementare le visualizzazioni di un video.
        Deve essere chiamato dal frontend ogni volta che il video viene effettivamente visualizzato.
        5/10 secondi controllo da frontend
        """
        video = self.get_object()
        video.views = models.F('views') + 1
        video.save(update_fields=['views'])
        video.refresh_from_db()  # aggiorna il valore da DB
        return Response({'views': video.views}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='popup-comments', permission_classes=[IsAuthenticated])
    def popup_comments(self, request, pk=None):
        """
        Restituisce i commenti popup per il video: per ogni timestamp unico,
        solo il commento con più like (minimo 1 like), ordinati per timestamp crescente.
        """
        video = self.get_object()
        comments = (
            Comment.objects
            .filter(video=video, is_disabled=False, timestamp_second__gt=0)
            .select_related('user')
            .annotate(like_count=Count('likes'))
            .filter(like_count__gte=1)
            .order_by('timestamp_second', '-like_count')
        )
        # Raggruppamento Python: per ogni timestamp, prendi solo il top comment
        seen = {}
        for c in comments:
            if c.timestamp_second not in seen:
                seen[c.timestamp_second] = c
        result = [
            {
                "timestamp": c.timestamp_second,
                "comment_id": c.id,
                "text": c.content,
                "author": c.user.username,
                "like_count": c.like_count,
            }
            for c in seen.values()
        ]
        serializer = PopupCommentSerializer(result, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='like', permission_classes=[OnlyUsersPermission])
    def like(self, request, pk=None):
        """Aggiunge un like al video dall'utente autenticato."""
        video = self.get_object()
        like, created = VideoLike.objects.get_or_create(user=request.user, video=video)
        if not created:
            return Response({"detail": "Hai già messo like"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"like_count": video.likes.count()})

    @action(detail=True, methods=['post'], url_path='unlike', permission_classes=[OnlyUsersPermission])
    def unlike(self, request, pk=None):
        """Rimuove il like dal video dell'utente autenticato."""
        video = self.get_object()
        try:
            like = VideoLike.objects.get(user=request.user, video=video)
            like.delete()
        except VideoLike.DoesNotExist:
            return Response({"detail": "Non hai messo like a questo video"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"like_count": video.likes.count()})

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
    filterset_fields = ['video']

    def get_queryset(self):
        """Esclude i commenti disabilitati per gli utenti normali."""
        return Comment.objects.filter(is_disabled=False).annotate(
            annotated_like_count=Count('likes', distinct=True)
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'], url_path='like', permission_classes=[OnlyUsersPermission])
    def like(self, request, pk=None):
        """Aggiunge un like al commento dall'utente autenticato."""
        comment = self.get_object()
        like, created = CommentLike.objects.get_or_create(user=request.user, comment=comment)
        if not created:
            return Response({"detail": "Hai già messo like"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"like_count": comment.likes.count()})

    @action(detail=True, methods=['post'], url_path='unlike', permission_classes=[OnlyUsersPermission])
    def unlike(self, request, pk=None):
        """Rimuove il like dal commento dell'utente autenticato."""
        comment = self.get_object()
        try:
            like = CommentLike.objects.get(user=request.user, comment=comment)
            like.delete()
        except CommentLike.DoesNotExist:
            return Response({"detail": "Non hai messo like a questo commento"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"like_count": comment.likes.count()})

    def handle_exception(self, exc):
        return handle_exception_with_serializer(exc)
    

#TODO rivedi authorization, forse solo per admin
class EndContestView(APIView):
    """
    Endpoint per chiudere il contest attivo e decretare il vincitore (con spareggio ponderato).
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

        videos = (
            Video.objects
            .filter(contest=contest)
            .annotate(avg_rating=Avg('ratings__value'))
        )
        if not videos.exists():
            return Response({"detail": "Nessun video presente per questo contest."}, status=status.HTTP_404_NOT_FOUND)

        # Trova la media voto massima
        max_rating = max([v.avg_rating for v in videos if v.avg_rating is not None])
        # Prendi tutti i video a pari merito
        top_videos = [v for v in videos if v.avg_rating == max_rating]

        if len(top_videos) == 1:
            winner = top_videos[0]
        else:
            # Spareggio avanzato
            winner = desempate_ponderato(top_videos)

        # Salva vincitore e chiudi il contest
        contest.winner = winner
        contest.is_closed = True
        closed_at_now = contest.closed_at = timezone.now()
        contest.save()

        winner_data = VideoSerializer(winner).data if winner else None

        # Se c'è stato spareggio, mostra anche la lista dei finalisti
        finalists_data = [VideoSerializer(v).data for v in top_videos] if len(top_videos) > 1 else None

        return Response({
            "contest": {
                "id": contest.id,
                "name": contest.name,
                "start_date": contest.start_date,
                "end_date": contest.end_date,
                "closed_at": closed_at_now,
                "winner_id": contest.winner.id if contest.winner else None
            },
            "winner": winner_data,
            "finalists": finalists_data
        }, status=status.HTTP_200_OK)


#TODO rivedi authorization
class ContestWinnersView(APIView):
    """
    Restituisce una lista paginata dei video vincitori
    dei contest passati (chiusi), ordinati dal contest più recente.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Prendi tutti i contest chiusi, con winner non null,
        # ordinati dal più recente
        contests = Contest.objects.filter(is_closed=True, winner__isnull=False).order_by('-closed_at')
        
        # Estraggo solo i video vincitori
        winners = [contest.winner for contest in contests if contest.winner is not None]

        # Applica la paginazione con il page_size globale
        paginator = PageNumberPagination()
        result_page = paginator.paginate_queryset(winners, request)

        # Serializzo la lista dei vincitori
        serializer = VideoSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)