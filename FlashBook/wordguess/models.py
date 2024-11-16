from django.db import models
from homepage.models import User

class WordGuessGame(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game_status = models.CharField(max_length=20, choices=[('in_progress', 'In Progress'), ('completed', 'Completed')], default='in_progress')
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Game {self.id} for {self.user.username}"
