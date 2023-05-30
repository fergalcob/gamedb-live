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
    path('accounts/profile/delete_review', views.delete_review, name='delete_review'),
    path('accounts/profile/edit_review', views.edit_review, name='edit_review'),
    path('accounts/profile/delete_reply', views.delete_reply, name='delete_reply'),
    path('accounts/profile/edit_reply', views.edit_reply, name='edit_reply'),
    path('accounts/profile', views.account_profile, name='profile'),
    path('accounts/profile/my_collection', views.my_collection, name='my_collection'),
    path('accounts/profile/reviews_comments',views.reviews_and_comments, name='reviews_comments'),
    path('accounts/profile/update_profile',views.update_profile, name='update_profile'),
    path('accounts/profile/submit_profile_changes',views.profile_changes, name='submit_profile_changes'),
    path('accounts/profile/remove_from_collection', views.remove_game_from_collection, name='remove_game_from_collection'),
    path('accounts/profile/my_lists', views.my_lists, name='my_lists'),
    path('accounts/profile/publish_list', views.publish_list, name='publish_list'),
    path('accounts/profile/unpublish_list', views.unpublish_list, name='unpublish_list'),
    path('accounts/profile/create_list', views.create_list, name='create_list'),

