from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # Add a field for default personality
    default_personality = models.CharField(max_length=50, blank=True, null=True)

    # Add a field for chat history (stored as JSON)
    chat_history = models.JSONField(default=list)

    def __str__(self):
        return self.username