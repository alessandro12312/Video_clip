# CommentLike model
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class CommentLike(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comment_likes",
        help_text="Utente che ha messo like al commento",
    )
    comment = models.ForeignKey(
        "Comment",
        on_delete=models.CASCADE,
        related_name="likes",
        help_text="Commento che ha ricevuto il like",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Data e ora del like",
    )

    class Meta:
        unique_together = ("user", "comment")
        ordering = ["-created_at"]
        verbose_name = "Like commento"
        verbose_name_plural = "Like commento"

    def __str__(self):
        return f"{self.user.username} likes comment {self.comment_id}"
