# Video model
import os
from django.db import models
from .user import User
from .contest import Contest



class Video(models.Model):
    title = models.CharField(max_length=100)
    file = models.FileField(upload_to='video/')
    uploader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_videos')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    contest = models.ForeignKey(Contest, on_delete=models.SET_NULL, null=True, blank=True, related_name="videos")
    views = models.IntegerField(default=0)
    tag = models.CharField(
        max_length=20,
        choices=Contest.Tag.choices,
        null=False, blank=False,
        help_text="Tag del video, deve corrispondere al contest",
        default=Contest.Tag.FUNNY  # Default value per evitare errori su record precedenti #TODO: rimuovere in produzione
    )
    duration = models.PositiveIntegerField(
        help_text="Durata del video in secondi",
        default=0   # Default value per evitare errori su record precedenti #TODO: rimuovere in produzione
    )

    def __str__(self):
        return self.title