from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from cs_clips.api.notifications.notification_serializers import NotificationSerializer
from cs_clips.models import Notification


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user).select_related(
            "sender", "video"
        )

    @extend_schema(
        summary="Lista notifiche dell'utente autenticato",
        description=(
            "Ritorna la lista paginata delle notifiche, ordinate per data decrescente."
        ),
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(exclude=True)
    def create(self, request, *args, **kwargs):
        return Response(
            {"detail": "Creazione diretta non permessa."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    @extend_schema(exclude=True)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Conteggio notifiche non lette",
        description=(
            "Ritorna il numero di notifiche non lette per l'utente autenticato."
        ),
        responses={
            200: {
                "type": "object",
                "properties": {"count": {"type": "integer"}},
            }
        },
    )
    @action(detail=False, methods=["get"], url_path="unread-count")
    def unread_count(self, request):
        count = self.get_queryset().filter(is_read=False).count()
        return Response({"count": count})

    @extend_schema(
        request=None,
        summary="Marca una notifica come letta",
        description=(
            "Marca la notifica specificata come letta. "
            "Ritorna 404 se non appartiene all'utente."
        ),
        responses={
            200: {
                "type": "object",
                "properties": {"detail": {"type": "string"}},
            }
        },
    )
    @action(detail=True, methods=["post"], url_path="mark-read")
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save(update_fields=["is_read"])
        return Response({"detail": "Notifica marcata come letta."})

    @extend_schema(
        request=None,
        summary="Marca tutte le notifiche come lette",
        description="Marca tutte le notifiche non lette dell'utente come lette.",
        responses={
            200: {
                "type": "object",
                "properties": {"detail": {"type": "string"}},
            }
        },
    )
    @action(detail=False, methods=["post"], url_path="mark-all-read")
    def mark_all_read(self, request):
        updated = self.get_queryset().filter(is_read=False).update(is_read=True)
        return Response({"detail": f"{updated} notifiche marcate come lette."})
