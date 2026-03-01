# Video model
from django.db import models

from .contest import Contest
from .user import User


class Video(models.Model):
    title = models.CharField(max_length=100)
    file = models.FileField(upload_to="")
    uploader = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="uploaded_videos"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    contest = models.ForeignKey(
        Contest, on_delete=models.SET_NULL, null=True, blank=True, related_name="videos"
    )
    views = models.IntegerField(default=0)
    tag = models.CharField(
        max_length=20,
        choices=Contest.Tag.choices,
        null=False,
        blank=False,
        help_text="Tag del video, deve corrispondere al contest",
        # #TODO: rimuovere default in produzione
        default=Contest.Tag.FUNNY,
    )
    duration = models.PositiveIntegerField(
        help_text="Durata del video in secondi",
        # #TODO: rimuovere default in produzione
        default=0,
    )
    allow_download = models.BooleanField(
        default=True,
        help_text="Consenti il download della clip ad altri utenti",
    )

    def __str__(self):
        return self.title
