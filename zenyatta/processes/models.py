from django.db import models


class Process(models.Model):
    title = models.CharField(max_length=150)
