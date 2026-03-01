from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models import Count, Exists, OuterRef, Value
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenRefreshSerializer,
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from cs_clips.api.users.user_serializers import (
    UserRegistrationSerializer,
    UserSerializer,
)
from cs_clips.permissions import OnlyUsersPermission, RoleBasedPermission

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        try:
            data = super().validate(attrs)
        except (AuthenticationFailed, InvalidToken, TokenError):
            raise AuthenticationFailed(
                "Nessun account attivo trovato con le credenziali fornite."
            )
        user = self.user

        # Aggiorna last_login
        user.last_login = timezone.now()
        user.save(update_fields=["last_login"])
        return data


class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        try:
            return super().validate(attrs)
        except (InvalidToken, TokenError):
            raise AuthenticationFailed("Il token è scaduto o non valido.")


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = CustomTokenRefreshSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("id")
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, RoleBasedPermission]

    def get_queryset(self):
        """Queryset con annotation per contatori e is_followed_by_me."""
        qs = User.objects.all().order_by("id")
        qs = qs.annotate(
            followers_count=Count("followers", distinct=True),
            following_count=Count("following", distinct=True),
        )
        if self.request.user.is_authenticated:
            qs = qs.annotate(
                is_followed_by_me=Exists(
                    User.objects.filter(
                        id=self.request.user.id,
                        following=OuterRef("pk"),
                    )
                )
            )
        else:
            qs = qs.annotate(is_followed_by_me=Value(False))
        return qs

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="page", type=int, required=False, description="Numero della pagina"
            ),
            OpenApiParameter(
                name="page_size",
                type=int,
                required=False,
                description="Numero di risultati per pagina",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_permissions(self):
        return [AllowAny()] if self.action == "create" else super().get_permissions()

    def get_serializer_class(self):
        return UserRegistrationSerializer if self.action == "create" else UserSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        # Assegna automaticamente l'utente al gruppo 'toconfirm'
        group, created = Group.objects.get_or_create(name="toconfirm")
        user.groups.add(group)

    @action(
        detail=False,
        methods=["get"],
        url_path="by-username/(?P<username>[^/.]+)",
    )
    def get_by_username(self, request, username=None):
        """Recupera un utente tramite username."""
        user = get_object_or_404(self.get_queryset(), username=username)
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=["post"],
        url_path="follow",
        permission_classes=[OnlyUsersPermission],
    )
    def follow(self, request, pk=None):
        """
        Permette all'utente autenticato di seguire un altro utente.
        """
        target_user = self.get_object()
        if request.user == target_user:
            return Response(
                {"detail": "Non puoi seguire te stesso."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        request.user.following.add(target_user)
        return Response(
            {
                "detail": f"Ora segui {target_user.username}.",
                "is_followed": True,
                "followers_count": target_user.followers.count(),
            }
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="unfollow",
        permission_classes=[OnlyUsersPermission],
    )
    def unfollow(self, request, pk=None):
        """
        Permette all'utente autenticato di smettere di seguire un altro utente.
        """
        target_user = self.get_object()
        request.user.following.remove(target_user)
        return Response(
            {
                "detail": f"Hai smesso di seguire {target_user.username}.",
                "is_followed": False,
                "followers_count": target_user.followers.count(),
            }
        )

    @action(detail=True, methods=["get"], url_path="followers")
    def get_followers(self, request, pk=None):
        """
        Restituisce la lista paginata degli utenti che seguono questo utente.
        """
        target_user = self.get_object()
        followers = self.get_queryset().filter(following=target_user)
        page = self.paginate_queryset(followers)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(followers, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="following")
    def get_following(self, request, pk=None):
        """
        Restituisce la lista paginata degli utenti che questo utente sta seguendo.
        """
        target_user = self.get_object()
        following = self.get_queryset().filter(followers=target_user)
        page = self.paginate_queryset(following)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(following, many=True)
        return Response(serializer.data)
