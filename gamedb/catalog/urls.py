from django.urls import path
from . import views
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path('games/<int:pk>', views.game_description_view, name='game-description'),
    path('search_results/', views.search_results, name='search_results'),
    path('register', views.register, name='register'),
    path('', include("django.contrib.auth.urls")),
    path('submit_review/<int:pk>', views.submit_review, name='submit_review'),
    path('submit_comment/<int:pk>', views.submit_comment, name='submit_comment'),
