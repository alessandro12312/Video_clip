# Rating model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .user import User
from .video import Video


class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ratings")
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name="ratings")
    value = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )  # Valore ridotto a 5
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (
            "user",
            "video",
        )  # Un utente può dare un solo rating per video

    def __str__(self):
        return f"{self.user.username} rated {self.video.title}: {self.value}"
