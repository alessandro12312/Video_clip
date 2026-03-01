from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from cs_clips.api.ratings.rating_serializers import RatingSerializer
from cs_clips.exceptions.error_handler import handle_exception_with_serializer
from cs_clips.models import Rating
from cs_clips.permissions import RoleBasedPermission


class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
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

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def handle_exception(self, exc):
        return handle_exception_with_serializer(exc)
