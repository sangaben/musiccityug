# artists/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, Count, Sum
from django.utils import timezone
from datetime import timedelta

from .models import Artist, Follow
from music.models import Song, Genre
from music.forms import SongUploadForm
from library.models import Like
from django.db.models.functions import Coalesce
from django.db.models import Value

def artists(request):
    """All artists page with popular and new sections"""
    # Get all verified artists with additional data
    artists_list = Artist.objects.filter(is_verified=True).annotate(
        total_songs=Count('songs', distinct=True),
        total_plays=Coalesce(Sum('songs__plays'), Value(0)),
        total_downloads=Coalesce(Sum('songs__downloads'), Value(0))
    ).select_related('user').order_by('-created_at')
    
    # Most popular artists (based on total plays + downloads)
    popular_artists = artists_list.annotate(
        popularity_score=Coalesce(Sum('songs__plays'), Value(0)) + Coalesce(Sum('songs__downloads'), Value(0))
    ).order_by('-popularity_score')[:12]
    
    # Newly added artists (most recent)
    new_artists = artists_list.order_by('-created_at')[:12]
    
    context = {
        'artists': artists_list,
        'popular_artists': popular_artists,
        'new_artists': new_artists,
        'title': 'All Artists'
    }
    return render(request, 'artists/artists.html', context)

def trending_artists(request):
    """Trending artists page"""
    seven_days_ago = timezone.now() - timedelta(days=7)
    trending_artists_list = Artist.objects.filter(
        is_verified=True
    ).annotate(
        weekly_plays=Sum(
            'songs__plays',
            filter=Q(songs__upload_date__gte=seven_days_ago)
        ),
        followers_count=Count('followers')
    ).filter(
        weekly_plays__isnull=False
    ).order_by('-weekly_plays')
    
    context = {
        'artists': trending_artists_list,
        'title': 'Trending Artists'
    }
    return render(request, 'artists/artists.html', context)

def artist_detail(request, artist_id):
    """Artist profile page"""
    artist = get_object_or_404(Artist, id=artist_id, is_verified=True)
    
    # Show ALL songs (both approved and unapproved) to everyone
    songs = Song.objects.filter(artist=artist).order_by('-upload_date')
    
    # Check if current user follows this artist
    is_following = False
    if request.user.is_authenticated:
        is_following = Follow.objects.filter(
            follower=request.user, 
            artist=artist
        ).exists()
    
    context = {
        'artist': artist,
        'songs': songs,
        'is_following': is_following,
        'songs_count': songs.count(),
        'total_plays': sum(song.plays for song in songs),
        'total_downloads': sum(song.downloads for song in songs),
        'followers_count': artist.followers.count(),
    }
    return render(request, 'artists/artist_detail.html', context)

@login_required
def artist_dashboard(request):
    """Artist dashboard"""
    try:
        artist = request.user.artist_profile
    except Artist.DoesNotExist:
        messages.error(request, "You need to be an artist to access the dashboard.")
        return redirect('home')

    # Get artist stats
    total_plays = artist.songs.aggregate(total=Sum('plays'))['total'] or 0
    total_downloads = artist.songs.aggregate(total=Sum('downloads'))['total'] or 0
    total_likes = Like.objects.filter(song__artist=artist).count()
    total_followers = Follow.objects.filter(artist=artist).count()

    # Get recent songs
    recent_songs = artist.songs.all().order_by('-upload_date')[:6]

    # Get top songs
    top_songs = artist.songs.all().order_by('-plays')[:5]

    # Get genres for upload form
    genres = Genre.objects.all()

    context = {
        'artist': artist,
        'total_plays': total_plays,
        'total_downloads': total_downloads,
        'total_likes': total_likes,
        'total_followers': total_followers,
        'recent_songs': recent_songs,
        'top_songs': top_songs,
        'genres': genres,
    }
    return render(request, 'artists/artist_dashboard.html', context)

@login_required
def upload_music(request):
    """Song upload for artists"""
    # Check if user is an artist
    try:
        artist_profile = Artist.objects.get(user=request.user)
    except Artist.DoesNotExist:
        messages.error(request, "You need to be an artist to upload music.")
        return redirect('discover')
    
    if request.method == 'POST':
        form = SongUploadForm(request.POST, request.FILES)
        
        if form.is_valid():
            try:
                song = form.save(commit=False)
                song.artist = artist_profile
                song.plays = 0
                song.downloads = 0
                song.is_approved = False
                
                # Handle file validation
                if 'audio_file' in request.FILES:
                    audio_file = request.FILES['audio_file']
                    
                    # Check file size (10MB limit)
                    if audio_file.size > 10 * 1024 * 1024:
                        messages.error(request, "Audio file must be less than 10MB")
                        return render(request, 'artists/upload_music.html', {
                            'form': form,
                            'genres': Genre.objects.all()
                        })
                    
                    # Check file extension
                    allowed_extensions = ['mp3', 'wav', 'ogg', 'm4a']
                    file_extension = audio_file.name.split('.')[-1].lower()
                    if file_extension not in allowed_extensions:
                        messages.error(request, f"File type not supported. Allowed: {', '.join(allowed_extensions)}")
                        return render(request, 'artists/upload_music.html', {
                            'form': form,
                            'genres': Genre.objects.all()
                        })
                
                song.save()
                messages.success(request, "Your song has been uploaded successfully and is pending review!")
                return redirect('my_uploads')
                
            except Exception as e:
                messages.error(request, f"Error saving song: {str(e)}")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = SongUploadForm()
    
    genres = Genre.objects.all()
    
    context = {
        'form': form,
        'genres': genres,
    }
    return render(request, 'artists/upload_music.html', context)

@login_required
def my_uploads(request):
    """Artist's uploaded songs"""
    # Check if user is an artist
    if not hasattr(request.user, 'userprofile') or not request.user.userprofile.is_artist:
        messages.error(request, "You need to be an artist to view uploads.")
        return redirect('discover')
    
    try:
        artist_profile = Artist.objects.get(user=request.user)
        songs = Song.objects.filter(artist=artist_profile).order_by('-upload_date')
    except Artist.DoesNotExist:
        messages.error(request, "Artist profile not found.")
        songs = []
    
    context = {
        'songs': songs,
    }
    return render(request, 'artists/my_uploads.html', context)

@csrf_exempt
@login_required
def follow_artist(request, artist_id):
    """API endpoint to follow/unfollow an artist"""
    if request.method == 'POST':
        artist = get_object_or_404(Artist, id=artist_id)
        follow, created = Follow.objects.get_or_create(
            follower=request.user,
            artist=artist
        )
        
        if not created:
            follow.delete()
        
        return JsonResponse({
            'followed': created,
            'followers_count': artist.followers.count()
        })
    
    return JsonResponse({'success': False})