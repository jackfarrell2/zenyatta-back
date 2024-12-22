from django.db import models


class Process(models.Model):
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title

class Step(models.Model):
    title = models.CharField(max_length=255)
    process = models.ForeignKey(
        Process,
        on_delete=models.SET_NULL,
        related_name='steps',
        null=True,
        blank=True
    )
    step_number = models.PositiveIntegerField()
    description = models.TextField(blank=True)
