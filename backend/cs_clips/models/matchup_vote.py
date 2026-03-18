from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class MatchupVote(models.Model):
    """Voto di un utente su un matchup bracket."""

    matchup = models.ForeignKey(
        "Matchup",
        on_delete=models.CASCADE,
        related_name="votes",
        help_text="Matchup votato",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="matchup_votes",
        help_text="Utente che ha votato",
    )
    entry = models.ForeignKey(
        "ContestEntry",
        on_delete=models.CASCADE,
        related_name="received_votes",
        help_text="Entry votata dall'utente",
    )
    value = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Voto da 1 a 5",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Data e ora del voto",
    )

    class Meta:
        unique_together = ("matchup", "user")
        ordering = ["-created_at"]
        verbose_name = "Voto matchup"
        verbose_name_plural = "Voti matchup"

    def __str__(self):
        return f"Voto {self.value} di {self.user} su matchup {self.matchup_id}"
