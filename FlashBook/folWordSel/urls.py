from django.urls import path
from folWordSel import views

urlpatterns = [
    path('',views.folder_view,name='folder'),
    path('add_folder/',views.add_folder,name='add_folder'),
    path('<int:folder_id>',views.word_view,name='word'),
    path('<int:folder_id>/select_game/',views.select_game_view,name='select_game'),
    path('<int:folder_id>/edit_folder',views.edit_folder,name='edit_folder'),
    path('<int:folder_id>/add_word',views.add_word,name='add_word'),
    path('<int:folder_id>/edit_word/<int:word_id>',views.edit_word,name='edit_word'),
]
