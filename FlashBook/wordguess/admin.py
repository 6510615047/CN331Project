
from django.contrib import admin
from .models import WordGuessGame

@admin.register(WordGuessGame)
class WordGuessGameAdmin(admin.ModelAdmin):
    list_display = ('user', 'game_status', 'start_time', 'end_time')
    list_filter = ('game_status', 'user')
    search_fields = ('user__username',)
