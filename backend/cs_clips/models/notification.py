from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Notification(models.Model):
    class Type(models.TextChoices):
        COMMENT_RECEIVED = "comment_received", "Commento ricevuto"
        LIKE_RECEIVED = "like_received", "Like ricevuto"
        COMMENT_PROMOTED = "comment_promoted", "Commento promosso a popup"
        CONTEST_OPENED = "contest_opened", "Nuovo contest aperto"
        BRACKET_INVITE = "bracket_invite", "Invito bracket"
        BRACKET_TURN = "bracket_turn", "Turno bracket disponibile"
        CONTEST_RESULTS = "contest_results", "Risultati contest"

    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications",
        help_text="Utente che riceve la notifica",
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_notifications",
        null=True,
        blank=True,
        help_text="Utente che ha generato l'evento (null per eventi di sistema)",
    )
    type = models.CharField(
        max_length=30,
        choices=Type.choices,
        help_text="Tipo di notifica",
    )
    is_read = models.BooleanField(
        default=False,
        help_text="Se la notifica è stata letta",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Data e ora di creazione",
    )
    video = models.ForeignKey(
        "Video",
        on_delete=models.SET_NULL,
        related_name="notifications",
        null=True,
        blank=True,
        help_text="Video collegato alla notifica (opzionale)",
    )
    comment = models.ForeignKey(
        "Comment",
        on_delete=models.SET_NULL,
        related_name="notifications",
        null=True,
        blank=True,
        help_text="Commento collegato alla notifica (opzionale)",
    )
    contest = models.ForeignKey(
        "Contest",
        on_delete=models.SET_NULL,
        related_name="notifications",
        null=True,
        blank=True,
        help_text="Contest collegato alla notifica (opzionale)",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Notifica"
        verbose_name_plural = "Notifiche"
        indexes = [
            models.Index(
                fields=["recipient", "-created_at"],
                name="idx_notif_recipient_date",
            ),
            models.Index(
                fields=["recipient", "is_read"],
                name="idx_notif_recipient_read",
            ),
        ]

    def __str__(self):
        return f"[{self.get_type_display()}] → {self.recipient.username}"
