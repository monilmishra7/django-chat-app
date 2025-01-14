from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.index, name='index'),
    path('chat/<int:user_id>/', views.room, name='room'),
    path('register/', views.register, name='register'),
]