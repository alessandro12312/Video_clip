from django.contrib.auth.models import Group
from django.utils import timezone
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from cs_clips.api.users.user_serializers import (
    UserRegistrationSerializer,
    UserSerializer,
)
from cs_clips.exceptions.error_handler import handle_exception_with_serializer
from cs_clips.models import User
from cs_clips.permissions import OnlyUsersPermission, RoleBasedPermission


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


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("id")
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, RoleBasedPermission]

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
            return Response({"detail": "Non puoi seguire te stesso."}, status=400)

        request.user.following.add(target_user)
        return Response({"detail": f"Hai iniziato a seguire {target_user.username}."})

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
        return Response({"detail": f"Hai smesso di seguire {target_user.username}."})

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
    @action(detail=True, methods=["get"], url_path="followers")
    def get_followers(self, request, pk=None):
        """
        Restituisce la lista degli utenti che seguono questo utente.
        """
        target_user = self.get_object()
        followers = target_user.followers.all()
        serializer = UserSerializer(followers, many=True)
        return Response(serializer.data)

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
    @action(detail=True, methods=["get"], url_path="following")
    def get_following(self, request, pk=None):
        """
        Restituisce la lista degli utenti che questo utente sta seguendo.
        """
        target_user = self.get_object()
        following = target_user.following.all()
        serializer = UserSerializer(following, many=True)
        return Response(serializer.data)

    def handle_exception(self, exc):
        return handle_exception_with_serializer(exc)
