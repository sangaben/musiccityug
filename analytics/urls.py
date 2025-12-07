from django.urls import path
from . import views

urlpatterns = [
    path('analytics/song/<int:song_id>/', views.song_analytics, name='song_analytics'),
    path('analytics/top-songs/', views.top_songs, name='top_songs'),
    path('analytics/song-stats/<int:song_id>/', views.get_song_stats, name='get_song_stats'),
]