from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import NewsArticle
from music.models import Song, Genre
from artists.models import Artist

def news_view(request):
    """Main news page"""
    # Get filter parameters
    category = request.GET.get('category', 'all')
    sort_by = request.GET.get('sort', 'latest')
    
    # Filter news articles
    if category == 'all':
        articles = NewsArticle.objects.filter(is_published=True)
    else:
        articles = NewsArticle.objects.filter(category=category, is_published=True)
    
    # Sort articles
    if sort_by == 'popular':
        articles = articles.order_by('-views')
    else:  # latest
        articles = articles.order_by('-published_date')
    
    # Pagination
    paginator = Paginator(articles, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get categories for filter
    categories = NewsArticle.objects.values_list('category', flat=True).distinct()
    
    context = {
        'articles': page_obj,
        'categories': categories,
        'current_category': category,
        'current_sort': sort_by,
        'featured_articles': NewsArticle.objects.filter(is_featured=True, is_published=True)[:3]
    }
    return render(request, 'news/news.html', context)

def news_category_view(request, category):
    """News by category"""
    articles = NewsArticle.objects.filter(category=category, is_published=True).order_by('-published_date')
    categories = NewsArticle.objects.values_list('category', flat=True).distinct()
    
    paginator = Paginator(articles, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'articles': page_obj,
        'categories': categories,
        'current_category': category,
        'current_sort': 'latest',
        'featured_articles': NewsArticle.objects.filter(is_featured=True, is_published=True)[:3]
    }
    return render(request, 'news/news.html', context)

def news_detail_view(request, news_id):
    """News article detail"""
    article = get_object_or_404(NewsArticle, id=news_id, is_published=True)
    
    # Increment view count
    article.views += 1
    article.save()
    
    # Get related articles
    related_articles = NewsArticle.objects.filter(
        category=article.category, 
        is_published=True
    ).exclude(id=article.id).order_by('-published_date')[:4]
    
    context = {
        'article': article,
        'related_articles': related_articles,
    }
    return render(request, 'news/news_detail.html', context)

def charts(request):
    """Main charts page showing various music charts"""
    
    # Get time filter
    time_filter = request.GET.get('time', 'weekly')
    genre_filter = request.GET.get('genre', 'all')
    
    # Base queryset for trending songs
    trending_songs = Song.objects.filter(is_approved=True)
    
    # Apply time filter
    if time_filter == 'weekly':
        start_date = timezone.now() - timedelta(days=7)
        trending_songs = trending_songs.filter(upload_date__gte=start_date)
    elif time_filter == 'monthly':
        start_date = timezone.now() - timedelta(days=30)
        trending_songs = trending_songs.filter(upload_date__gte=start_date)
    
    # Apply genre filter
    if genre_filter != 'all':
        trending_songs = trending_songs.filter(genre__name=genre_filter)
    
    # Get top songs by plays
    top_songs = trending_songs.order_by('-plays')[:20]
    
    # Get top artists - SAFE VERSION
    top_artists = Artist.objects.filter(
        songs__in=trending_songs
    ).annotate(
        total_plays=Count('songs__plays'),
        song_count=Count('songs')
    ).filter(
        id__isnull=False,
        song_count__gt=0
    ).distinct().order_by('-total_plays')[:10]
    
    # Get trending news related to charts
    chart_news = NewsArticle.objects.filter(
        category='charts',
        is_published=True
    ).order_by('-published_date')[:5]
    
    # Get genres for filter
    genres = Genre.objects.all()
    
    context = {
        'top_songs': top_songs,
        'top_artists': top_artists,
        'chart_news': chart_news,
        'time_filter': time_filter,
        'genre_filter': genre_filter,
        'genres': genres,
        'current_time_filter': time_filter,
        'current_genre_filter': genre_filter,
    }
    
    return render(request, 'news/charts.html', context)

def top_songs(request):
    """Detailed top songs chart"""
    time_filter = request.GET.get('time', 'weekly')
    genre_filter = request.GET.get('genre', 'all')
    page = request.GET.get('page', 1)
    
    songs = Song.objects.filter(is_approved=True)
    
    # Apply filters
    if time_filter == 'weekly':
        start_date = timezone.now() - timedelta(days=7)
        songs = songs.filter(upload_date__gte=start_date)
    elif time_filter == 'monthly':
        start_date = timezone.now() - timedelta(days=30)
        songs = songs.filter(upload_date__gte=start_date)
    
    if genre_filter != 'all':
        songs = songs.filter(genre__name=genre_filter)
    
    # Order by popularity metrics
    songs = songs.order_by('-plays', '-downloads')
    
    # Pagination
    paginator = Paginator(songs, 20)
    songs_page = paginator.get_page(page)
    
    genres = Genre.objects.all()
    
    context = {
        'songs': songs_page,
        'time_filter': time_filter,
        'genre_filter': genre_filter,
        'genres': genres,
        'current_time_filter': time_filter,
        'current_genre_filter': genre_filter,
    }
    
    return render(request, 'news/top_songs.html', context)

def top_artists(request):
    """Detailed top artists chart"""
    time_filter = request.GET.get('time', 'weekly')
    page = request.GET.get('page', 1)
    
    # Get artists with their song statistics - FIXED: Ensure valid data
    artists = Artist.objects.filter(
        id__isnull=False  # Ensure artist has an ID
    ).annotate(
        total_plays=Count('songs__plays'),
        total_downloads=Count('songs__downloads'),
        song_count=Count('songs')
    ).filter(
        song_count__gt=0,  # Only artists with songs
        total_plays__gt=0  # Only artists with plays
    )
    
    # Apply time filter to songs
    if time_filter == 'weekly':
        start_date = timezone.now() - timedelta(days=7)
        artists = artists.filter(songs__upload_date__gte=start_date)
    elif time_filter == 'monthly':
        start_date = timezone.now() - timedelta(days=30)
        artists = artists.filter(songs__upload_date__gte=start_date)
    
    artists = artists.order_by('-total_plays', '-total_downloads')[:50]
    
    # Pagination
    paginator = Paginator(artists, 20)
    artists_page = paginator.get_page(page)
    
    context = {
        'artists': artists_page,
        'time_filter': time_filter,
        'current_time_filter': time_filter,
    }
    
    return render(request, 'news/top_artists.html', context)

def new_releases(request):
    """New releases chart"""
    time_filter = request.GET.get('time', 'weekly')  # weekly, monthly
    genre_filter = request.GET.get('genre', 'all')
    page = request.GET.get('page', 1)
    
    # Determine date range
    if time_filter == 'weekly':
        start_date = timezone.now() - timedelta(days=7)
    else:  # monthly
        start_date = timezone.now() - timedelta(days=30)
    
    new_songs = Song.objects.filter(
        is_approved=True,
        upload_date__gte=start_date
    )
    
    if genre_filter != 'all':
        new_songs = new_songs.filter(genre__name=genre_filter)
    
    new_songs = new_songs.order_by('-upload_date', '-plays')
    
    # Pagination
    paginator = Paginator(new_songs, 20)
    songs_page = paginator.get_page(page)
    
    genres = Genre.objects.all()
    
    context = {
        'songs': songs_page,
        'time_filter': time_filter,
        'genre_filter': genre_filter,
        'genres': genres,
        'current_time_filter': time_filter,
        'current_genre_filter': genre_filter,
    }
    
    return render(request, 'news/new_releases.html', context)

# FIXED VERSION: Using genre_id instead of slug
def genre_charts(request, genre_id):
    """Genre-specific charts - FIXED to use genre_id instead of slug"""
    genre = get_object_or_404(Genre, id=genre_id)
    time_filter = request.GET.get('time', 'weekly')
    page = request.GET.get('page', 1)
    
    songs = Song.objects.filter(
        genre=genre,
        is_approved=True
    )
    
    # Apply time filter
    if time_filter == 'weekly':
        start_date = timezone.now() - timedelta(days=7)
        songs = songs.filter(upload_date__gte=start_date)
    elif time_filter == 'monthly':
        start_date = timezone.now() - timedelta(days=30)
        songs = songs.filter(upload_date__gte=start_date)
    
    songs = songs.order_by('-plays', '-downloads')[:50]
    
    # Pagination
    paginator = Paginator(songs, 20)
    songs_page = paginator.get_page(page)
    
    # Get other genres for navigation
    genres = Genre.objects.all()
    
    context = {
        'genre': genre,
        'songs': songs_page,
        'time_filter': time_filter,
        'genres': genres,
        'current_time_filter': time_filter,
    }
    
    return render(request, 'news/genre_charts.html', context)

# ADDITIONAL VIEW: If you want to access by genre name instead of ID
def genre_charts_by_name(request, genre_name):
    """Genre-specific charts accessed by genre name"""
    genre = get_object_or_404(Genre, name=genre_name)
    time_filter = request.GET.get('time', 'weekly')
    page = request.GET.get('page', 1)
    
    songs = Song.objects.filter(
        genre=genre,
        is_approved=True
    )
    
    # Apply time filter
    if time_filter == 'weekly':
        start_date = timezone.now() - timedelta(days=7)
        songs = songs.filter(upload_date__gte=start_date)
    elif time_filter == 'monthly':
        start_date = timezone.now() - timedelta(days=30)
        songs = songs.filter(upload_date__gte=start_date)
    
    songs = songs.order_by('-plays', '-downloads')[:50]
    
    # Pagination
    paginator = Paginator(songs, 20)
    songs_page = paginator.get_page(page)
    
    # Get other genres for navigation
    genres = Genre.objects.all()
    
    context = {
        'genre': genre,
        'songs': songs_page,
        'time_filter': time_filter,
        'genres': genres,
        'current_time_filter': time_filter,
    }
    
    return render(request, 'news/genre_charts.html', context)