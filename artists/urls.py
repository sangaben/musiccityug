from django.urls import path
from . import views

urlpatterns = [
    path('artists/', views.artists, name='artists'),
    path('artists/trending/', views.trending_artists, name='trending_artists'),
    path('artist/<int:artist_id>/', views.artist_detail, name='artist_detail'),
    path('dashboard/', views.artist_dashboard, name='artist_dashboard'),
    path('upload/', views.upload_music, name='upload_music'),
    path('my-uploads/', views.my_uploads, name='my_uploads'),
    path('follow/<int:artist_id>/', views.follow_artist, name='follow_artist'),
]