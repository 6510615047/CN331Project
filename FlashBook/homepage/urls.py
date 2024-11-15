from django.urls import path
from homepage import views

urlpatterns = [
    path('',views.homepage,name='homepage'),
    path('about/',views.about,name='about'),
    path('register/', views.register, name='register'),
    path('login/', views.login_views, name='login'),
    path('logout/', views.logout_views, name='logout'),
    path('dashboard/', views.user_dashboard, name='user_dashboard')
]