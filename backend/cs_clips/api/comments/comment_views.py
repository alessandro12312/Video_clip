from django.db.models import BooleanField, Count, Exists, OuterRef, Value
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from cs_clips.api.comments.comment_serializers import CommentSerializer
from cs_clips.exceptions.error_handler import handle_exception_with_serializer
from cs_clips.exceptions.error_response_serializer import ErrorResponseSerializer
from cs_clips.models import Comment, CommentLike
from cs_clips.permissions import OnlyUsersPermission, RoleBasedPermission


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.filter(is_disabled=False)
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, RoleBasedPermission]
    filterset_fields = ["video"]
    http_method_names = ["get", "post", "delete", "head", "options"]

    def get_queryset(self):
        """Queryset con annotazioni like_count e is_liked_by_me."""
        qs = Comment.objects.filter(is_disabled=False).annotate(
            like_count=Count("likes", distinct=True),
        )
        if self.request.user.is_authenticated:
            qs = qs.annotate(
                is_liked_by_me=Exists(
                    CommentLike.objects.filter(
                        comment=OuterRef("pk"), user=self.request.user
                    )
                ),
            )
        else:
            qs = qs.annotate(
                is_liked_by_me=Value(False, output_field=BooleanField()),
            )
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

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @extend_schema(
        request=None,
        responses={
            201: {"type": "object", "properties": {"detail": {"type": "string"}}},
            204: None,
            404: ErrorResponseSerializer,
            409: ErrorResponseSerializer,
        },
        summary="Like/unlike un commento",
        description="POST per mettere like, DELETE per rimuovere il like.",
    )
    @action(
        detail=True,
        methods=["post", "delete"],
        url_path="like",
        permission_classes=[IsAuthenticated, OnlyUsersPermission],
    )
    def like(self, request, pk=None):
        """Mette o rimuove like a un commento."""
        comment = self.get_object()
        if request.method == "POST":
            CommentLike.objects.create(user=request.user, comment=comment)
            return Response(
                {"detail": "Like aggiunto."}, status=status.HTTP_201_CREATED
            )
        # DELETE
        deleted, _ = CommentLike.objects.filter(
            user=request.user, comment=comment
        ).delete()
        if not deleted:
            raise NotFound("Like non trovato.")
        return Response(status=status.HTTP_204_NO_CONTENT)

    def handle_exception(self, exc):
        return handle_exception_with_serializer(exc)
