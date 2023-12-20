from django.urls import path
from . import views

urlpatterns = [
    path("", views.gamestart, name="gamestart"),
    path('create_thread', views.create_thread, name='create_thread'),
    path("turtlesoupgame", views.turtlesoupgame, name="turtlesoupgame"),
    path("escapegame", views.escapegame, name="escapegame"),
]