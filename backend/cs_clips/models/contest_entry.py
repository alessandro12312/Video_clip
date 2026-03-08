from django.conf import settings
from django.db import models


class ContestEntry(models.Model):
    """Iscrizione di un utente a un torneo bracket."""

    bracket = models.ForeignKey(
        "Bracket",
        on_delete=models.CASCADE,
        related_name="entries",
        help_text="Torneo a cui l'utente si iscrive",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bracket_entries",
        help_text="Utente iscritto al torneo",
    )
    video = models.ForeignKey(
        "Video",
        on_delete=models.CASCADE,
        related_name="bracket_entries",
        help_text="Video presentato per il torneo",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Data e ora di iscrizione",
    )

    class Meta:
        unique_together = ("bracket", "user")
        ordering = ["-created_at"]
        verbose_name = "Iscrizione torneo"
        verbose_name_plural = "Iscrizioni torneo"

    def __str__(self):
        return f"{self.user} - {self.bracket}"
