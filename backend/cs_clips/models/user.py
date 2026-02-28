# User model
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField("email address", unique=True, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Aggiunta relazione follower
    following = models.ManyToManyField(
        "self",
        symmetrical=False,
        related_name="followers",
        blank=True,
        help_text="Utenti che questo utente sta seguendo",
    )

    groups = models.ManyToManyField(
        "auth.Group",
        verbose_name="groups",
        blank=False,
        help_text="The groups this user belongs to.",
        related_name="custom_user_set",
        related_query_name="custom_user",
    )

    user_permissions = models.ManyToManyField(
        "auth.Permission",
        verbose_name="user permissions",
        blank=True,
        help_text="Specific permissions for this user.",
        related_name="custom_user_permissions_set",
        related_query_name="custom_user_permission",
    )

    def __str__(self):
        return self.username
