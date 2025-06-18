# Contest model
from django.db import models


class Contest(models.Model):
    class Tag(models.TextChoices):
        CLUTCH = 'clutch', 'Clutch'
        FUNNY = 'funny', 'Funny'
        FAIL = 'fail', 'Fail'

    name = models.CharField(max_length=100)
    tag = models.CharField(
        max_length=20,
        choices=Tag.choices,
        null=False, blank=False,
        help_text="Tag che identifica la categoria del contest",
        default=Tag.FUNNY   # Default value per evitare errori su record precedenti #TODO: rimuovere in produzione
    )
    start_date = models.DateField()
    end_date = models.DateField()
    winner = models.ForeignKey('Video', null=True, blank=True, on_delete=models.SET_NULL, related_name='won_contests')
    is_closed = models.BooleanField(default=False)  # principalmente per test
    closed_at = models.DateTimeField(null=True, blank=True) # principalmente per test

    class Meta:
        unique_together = ('start_date', 'end_date', 'tag')

    def __str__(self):
        return f"Contest {self.name} ({self.start_date} - {self.end_date})"