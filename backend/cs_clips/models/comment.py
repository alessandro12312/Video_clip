# Comment model
from django.db import models

from .user import User
from .video import Video


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    timestamp_second = models.PositiveIntegerField(
        help_text=(
            "Secondo del video a cui si riferisce il commento (>=0, <= durata video)"
        ),
        # #TODO: rimuovere default in produzione
        default=0,
    )
    is_disabled = models.BooleanField(
        default=False,
        help_text="Se True, il commento è nascosto dalle risposte API (moderazione)",
    )

    def __str__(self):
        return (
            f"{self.user.username} commented on "
            f"{self.video.title} at {self.timestamp_second}s"
        )
