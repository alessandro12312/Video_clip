from django.db import models


class Matchup(models.Model):
    """Singolo scontro tra due partecipanti in un turno del bracket."""

    bracket = models.ForeignKey(
        "Bracket",
        on_delete=models.CASCADE,
        related_name="matchups",
        help_text="Torneo a cui appartiene il matchup",
    )
    round_number = models.PositiveIntegerField(
        help_text="Numero del turno (1 = primo turno)",
    )
    position = models.PositiveIntegerField(
        help_text="Posizione del matchup nel turno",
    )
    entry_1 = models.ForeignKey(
        "ContestEntry",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="matchups_as_entry1",
        help_text="Primo partecipante",
    )
    entry_2 = models.ForeignKey(
        "ContestEntry",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="matchups_as_entry2",
        help_text="Secondo partecipante",
    )
    winner = models.ForeignKey(
        "ContestEntry",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="matchups_won",
        help_text="Vincitore del matchup",
    )
    is_completed = models.BooleanField(
        default=False,
        help_text="Indica se il matchup e' stato completato",
    )

    class Meta:
        unique_together = ("bracket", "round_number", "position")
        ordering = ["round_number", "position"]
        verbose_name = "Matchup"
        verbose_name_plural = "Matchup"

    def __str__(self):
        return f"{self.bracket} - Turno {self.round_number}, Pos {self.position}"
