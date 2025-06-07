# Entities for the database
import os
from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator

# User model
class User(AbstractUser):
    email = models.EmailField('email address', unique=True, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=False,
        help_text='The groups this user belongs to.',
        related_name='custom_user_set',
        related_query_name='custom_user'
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='custom_user_permissions_set',
        related_query_name='custom_user_permission'
    )

    def __str__(self):
        return self.username


# Contest model
class Contest(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    winner = models.ForeignKey('Video', null=True, blank=True, on_delete=models.SET_NULL, related_name='won_contests')
    is_closed = models.BooleanField(default=False)  # principalmente per test
    closed_at = models.DateTimeField(null=True, blank=True) # principalmente per test

    def __str__(self):
        return f"Contest {self.name} ({self.start_date} - {self.end_date})"

    
# Video model
class Video(models.Model):
    title = models.CharField(max_length=100)
    file = models.FileField(upload_to='videos/')
    uploader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_videos')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    contest = models.ForeignKey(Contest, on_delete=models.SET_NULL, null=True, blank=True, related_name="videos")
    views = models.IntegerField(default=0)
    tags = models.CharField(max_length=200, blank=True, help_text="Comma-separated tags to classify the video")


    def __str__(self):
        return self.title

    def delete(self, *args, **kwargs):
        """
        Cancella il file fisico associato nella cartella media/videos/
        quando il video viene eliminato dal database.
        """
        # Prima cancella il file, poi il record
        if self.file and os.path.isfile(self.file.path):
            os.remove(self.file.path)
        super().delete(*args, **kwargs)
        

# Rating model
class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='ratings')
    value = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'video')  # Un utente può dare un solo rating per video

    def __str__(self):
        return f"{self.user.username} rated {self.video.title}: {self.value}"


# Comment model
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} commented on {self.video.title}"
