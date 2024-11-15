from django.db import models
from django.contrib.auth.models import User  # or import your custom User model from homepage

class WordGuessGame(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    word = models.CharField(max_length=100)
    guesses = models.JSONField(default=list)
    incorrect_guesses = models.JSONField(default=list)
    game_status = models.CharField(max_length=50, default='in_progress')  # e.g., 'win', 'lose', 'in_progress'
    attempts_left = models.IntegerField(default=6)

    def __str__(self):
        return f"Game for {self.user.username} - Word: {self.word} - Status: {self.game_status}"
