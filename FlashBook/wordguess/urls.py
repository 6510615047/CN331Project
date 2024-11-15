from django.urls import path
from . import views

urlpatterns = [
    path('', views.word_guess_view, name='word_guess'),
]