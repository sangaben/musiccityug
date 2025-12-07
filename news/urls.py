from django.urls import path
from . import views

urlpatterns = [
    path('news/', views.news_view, name='news'),
    path('news/category/<str:category>/', views.news_category_view, name='news_category'),
    path('news/<int:news_id>/', views.news_detail_view, name='news_detail'),
    path('charts/', views.charts, name='charts'),
    path('charts/top-songs/', views.top_songs, name='top_songs'),
    path('charts/top-artists/', views.top_artists, name='top_artists'),
    path('charts/new-releases/', views.new_releases, name='new_releases'),
    # CHANGE THIS: Use genre_id instead of genre_slug
    path('charts/genre/<int:genre_id>/', views.genre_charts, name='genre_charts'),
]