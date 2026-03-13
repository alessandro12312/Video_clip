# VideoLike model
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class VideoLike(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="video_likes",
        help_text="Utente che ha messo like al video",
    )
    video = models.ForeignKey(
        "Video",
        on_delete=models.CASCADE,
        related_name="likes",
        help_text="Video che ha ricevuto il like",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Data e ora del like",
    )

    class Meta:
        unique_together = ("user", "video")
        ordering = ["-created_at"]
        verbose_name = "Like video"
        verbose_name_plural = "Like video"

    def __str__(self):
        return f"{self.user.username} likes {self.video.title}"
