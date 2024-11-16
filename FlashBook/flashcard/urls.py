from django.urls import path, include
from . import views

urlpatterns = [
    path('',views.flashcard,name='flashcard'),
    path('correct/',views.correct_answer,name="correct_answer"),
    path('wrong/',views.wrong_answer,name="wrong_answer"),
    path('next_word/',views.next_word,name="next_word"),
    path('finish/',views.finish,name="finish")
]
