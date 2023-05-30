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
    path('add_button', views.add_button, name='add_button'),
    path('accounts/profile', views.account_profile, name='profile'),
    path('accounts/profile/my_collection', views.my_collection, name='my_collection'),
    path('submit_review/<int:pk>', views.submit_review, name='submit_review'),
    path('submit_comment/<int:pk>', views.submit_comment, name='submit_comment'),
    path('tinymce/', include('tinymce.urls')),
    path('genres/all_genres', views.genre_list, name='genre_list'),
    path('genres/<int:genre_identifier>', views.genre_items, name='genre_items'),
    path('developers/<int:company_identifier>', views.developer_items, name='developer_items'),
    path('publishers/<int:company_identifier>', views.publisher_items, name='publisher_items'),
    path('ratings/', include('star_ratings.urls', namespace='ratings')),
    path('developers/all_developers', views.developer_list, name='all_developers'),
    path('publishers/all_publishers', views.publisher_list, name='all_publishers'),
    path('accounts/profile/my_lists', views.my_lists, name='my_lists'),
    path('accounts/profile/publish_list', views.publish_list, name='publish_list'),
    path('accounts/profile/unpublish_list', views.unpublish_list, name='unpublish_list'),
    path('accounts/profile/create_list', views.create_list, name='create_list'),
    path('add_to_list', views.add_to_list, name='add_to_list'),
    path('remove_from_list', views.remove_game_from_list, name='remove_from_list'),
    path('all_lists', views.all_lists, name='all_lists'),
    path('accounts/profile/update_profile_picture', views.profile_picture ,name='profile_uploader'),
    path('lists/<int:pk>', views.view_list, name='view_list'),
    path('accounts/change_password/', views.change_password, name='change_password'),
    path('lists/remove_from_list/<int:pk>', views.remove_game, name='remove_game'),
    path('accounts/profile/delete_review', views.delete_review, name='delete_review'),
    path('accounts/profile/edit_review', views.edit_review, name='edit_review'),
    path('accounts/profile/delete_reply', views.delete_reply, name='delete_reply'),
    path('accounts/profile/edit_reply', views.edit_reply, name='edit_reply'),
    path('accounts/profile/reviews_comments',views.reviews_and_comments, name='reviews_comments'),
    path('accounts/profile/update_profile',views.update_profile, name='update_profile'),
    path('accounts/profile/submit_profile_changes',views.profile_changes, name='submit_profile_changes'),
    path('accounts/profile/remove_from_collection', views.remove_game_from_collection, name='remove_game_from_collection'),
    path('lists/edit_list/<int:pk>', views.edit_list, name='edit_list'),
    path('lists/delete_list', views.delete_list, name='delete_list'),
]






