from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('discover/', views.discover, name='discover'),
    path('search/', views.search, name='search'),
    path('genres/', views.genres, name='genres'),
    path('genre/<int:genre_id>/', views.genre_songs, name='genre_songs'),
    path('song/<int:song_id>/', views.song_detail, name='song_detail'),
    
    # Player endpoints
    path('play-song/<int:song_id>/', views.play_song, name='play_song'),
    path('download-song/<int:song_id>/', views.download_song, name='download_song'),
    
    # API endpoints
    path('api/track-anonymous-play/<int:song_id>/', views.track_anonymous_play, name='track_anonymous_play'),
    path('api/update-play-duration/<int:song_id>/', views.update_play_duration, name='update_play_duration'),
    path('api/track-partial-play/<int:song_id>/', views.track_partial_play, name='track_partial_play'),
    path('api/track-download/', views.track_download, name='track_download'),
    path('like-song/<int:song_id>/', views.like_song, name='like_song'),
    
    # Charts/top songs
    path('top-songs/', views.top_songs, name='top_songs'),
    
    # ========== ADDED: NEW PLAY TRACKING ENDPOINTS ==========
    path('api/track-play/<int:song_id>/', views.track_play, name='track_play'),
    path('api/get-song-plays/<int:song_id>/', views.get_song_plays, name='get_song_plays'),
    path('api/bulk-update-plays/', views.bulk_update_plays, name='bulk_update_plays'),
    path('api/increment-plays-direct/<int:song_id>/', views.increment_plays_direct, name='increment_plays_direct'),
    # =========================================================
]