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
    path('search_folder',views.search_folder,name='search_folder'),
    path('<int:folder_id>/search_word',views.search_word,name='search_word'),
    # path('selectGame/', views.select_game_view, name='select_game'),
    path('timeSet/', views.time_set_view, name='time_set'),  # เพิ่มเส้นทางนี้
    path('modeSet/', views.mode_set_view, name='mode_set'),  # เพิ่มเส้นทางนี้
]
 