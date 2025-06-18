from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from cs_clips.permissions import RoleBasedPermission
from cs_clips.exceptions.error_handler import handle_exception_with_serializer
from cs_clips.models import Comment
from cs_clips.api.comments.comment_serializers import CommentSerializer



class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, RoleBasedPermission]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def handle_exception(self, exc):
        return handle_exception_with_serializer(exc)