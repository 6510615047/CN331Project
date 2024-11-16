from django.urls import path
from . import views

urlpatterns = [
    path('', views.word_guess_view, name='word_guess'),
    path('scores/<int:game_id>/', views.game_scores_view, name='game_scores'),
]