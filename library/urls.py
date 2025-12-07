from django.urls import path
from . import views

urlpatterns = [
    path('library/', views.library, name='library'),
    path('playlists/', views.playlists, name='playlists'),
    path('playlist/<int:playlist_id>/', views.playlist_detail, name='playlist_detail'),
    path('liked-songs/', views.liked_songs, name='liked_songs'),
    path('recently-played/', views.recently_played, name='recently_played'),
    path('like-song/<int:song_id>/', views.like_song, name='like_song'),
    path('playlist/<int:playlist_id>/remove/<int:song_id>/', views.remove_from_playlist, name='remove_from_playlist'),
    path('playlist/<int:playlist_id>/delete/', views.delete_playlist, name='delete_playlist'),
    path('add-to-playlist/<int:song_id>/', views.add_to_playlist, name='add_to_playlist'),
]