from django.conf import settings
from django.db import models


class Bracket(models.Model):
    """Torneo bracket a eliminazione diretta."""

    class Status(models.TextChoices):
        REGISTRATION = "registration", "Registrazione aperta"
        ACTIVE = "active", "Torneo in corso"
        COMPLETED = "completed", "Torneo completato"

    name = models.CharField(
        max_length=200,
        help_text="Nome del torneo",
    )
    description = models.TextField(
        blank=True,
        help_text="Descrizione del torneo",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.REGISTRATION,
        help_text="Stato attuale del torneo",
    )
    max_participants = models.PositiveIntegerField(
        help_text="Numero massimo di partecipanti",
    )
    current_round = models.PositiveIntegerField(
        default=1,
        help_text="Turno attuale del torneo",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_brackets",
        help_text="Admin che ha creato il torneo",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Data e ora di creazione",
    )
    prize_description = models.TextField(
        blank=True,
        help_text="Descrizione del premio per il vincitore",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Bracket"
        verbose_name_plural = "Bracket"

    def __str__(self):
        return self.name
