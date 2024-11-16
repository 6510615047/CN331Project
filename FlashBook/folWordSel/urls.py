from django.urls import path
from folWordSel import views

urlpatterns = [
    path('', views.folder_view, name='folder'),
    path('word/', views.word_view, name='word'),
    path('selectGame/', views.select_game_view, name='select_game'),
    path('timeSet/', views.time_set_view, name='time_set'),  # เพิ่มเส้นทางนี้
    path('modeSet/', views.mode_set_view, name='mode_set'),  # เพิ่มเส้นทางนี้
]
