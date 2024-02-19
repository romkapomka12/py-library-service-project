from django.db import models


class Book(models.Model):
    class CoverChoices(models.TextChoices):
        HARD = "HARD"
        SOFT = "SOFT"
    title = models.CharField(max_length=120)
    author = models.CharField(max_length=60)
    cover = models.CharField(max_length=4, choices=CoverChoices.choices)
    inventory = models.PositiveIntegerField(default=0)
    daily_free = models.DecimalField(max_digits=7, decimal_places=2)

    def __str__(self) -> str:
        return self.title
