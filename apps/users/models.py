from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    position = models.CharField(max_length=100, default='Visitor', blank=True)

    def __str__(self):
        return self.username