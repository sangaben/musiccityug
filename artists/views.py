# artists/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q, Count, Sum, Case, When, IntegerField
from django.db.models.functions import Coalesce
from django.utils import timezone
from datetime import timedelta
import json

from .models import Artist, Follow
from music.models import Song, Genre, SongPlay, SongDownload
from music.forms import SongUploadForm
from library.models import Like

# Earnings rates
STREAM_RATE = 0.001  # $0.001 per play
DOWNLOAD_RATE = 0.003  # $0.003 per download

def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@require_POST
@login_required
def play_song(request, song_id):
    """Play song and increment play count"""
    song = get_object_or_404(Song, id=song_id)
    
    # Check access for premium content
    if not song.can_be_accessed_by(request.user):
        return JsonResponse({
            'error': 'Premium content requires subscription',
            'can_preview': getattr(song, 'preview_duration', 0) > 0,
            'preview_duration': getattr(song, 'preview_duration', 0)
        }, status=403)
    
    # Increment play count
    song.plays += 1
    song.save()
    
    # Record play in SongPlay model
    play = SongPlay.objects.create(
        song=song,
        user=request.user,
        ip_address=get_client_ip(request),
        duration_played=0,
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        audio_quality='high' if hasattr(request.user, 'userprofile') and request.user.userprofile.is_premium else 'standard'
    )
    
    return JsonResponse({
        'success': True,
        'id': song.id,
        'title': song.title,
        'artist': song.artist.name,
        'artist_id': song.artist.id,
        'cover': song.cover_image.url if song.cover_image else '/static/images/default-cover.jpg',
        'audio': song.audio_file.url,
        'duration': getattr(song, 'duration', '3:45'),
        'plays': song.plays,
        'is_premium': getattr(song, 'is_premium_only', False),
        'play_id': play.id
    })

@require_POST
@login_required
def like_song(request, song_id):
    """Like/unlike a song"""
    song = get_object_or_404(Song, id=song_id, is_approved=True)
    
    like, created = Like.objects.get_or_create(user=request.user, song=song)
    
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
    
    like_count = song.likes.count()
    
    return JsonResponse({
        'success': True,
        'liked': liked,
        'like_count': like_count
    })

@login_required
def download_song(request, song_id):
    """Download song"""
    song = get_object_or_404(Song, id=song_id, is_approved=True)
    
    if not song.can_be_accessed_by(request.user):
        return JsonResponse({
            'success': False,
            'error': 'Premium content requires subscription'
        }, status=403)
    
    song.downloads += 1
    song.save()
    
    SongDownload.objects.create(
        song=song,
        user=request.user,
        ip_address=get_client_ip(request),
        file_size=song.audio_file.size
    )
    
    return JsonResponse({
        'success': True,
        'download_url': song.audio_file.url,
        'filename': f"{song.title} - {song.artist.name}.mp3"
    })

@require_POST
@login_required
def update_play_duration(request, song_id):
    """Update play duration when playback ends"""
    try:
        data = json.loads(request.body)
        duration_played = data.get('duration_played', 0)
        play_id = data.get('play_id')
        
        if play_id:
            play = SongPlay.objects.get(id=play_id, user=request.user)
            play.duration_played = duration_played
            play.save()
        else:
            play = SongPlay.objects.filter(
                song_id=song_id,
                user=request.user
            ).order_by('-played_at').first()
            
            if play:
                play.duration_played = duration_played
                play.save()
                
        return JsonResponse({'success': True})
        
    except (json.JSONDecodeError, SongPlay.DoesNotExist):
        return JsonResponse({'success': False, 'error': 'Invalid data'})

@require_POST
@login_required
def follow_artist_from_music(request, artist_id):
    """API endpoint to follow/unfollow an artist from music pages"""
    try:
        artist = get_object_or_404(Artist, id=artist_id, is_verified=True)
        
        if hasattr(request.user, 'artist_profile') and request.user.artist_profile == artist:
            return JsonResponse({
                'success': False,
                'error': 'You cannot follow yourself'
            }, status=400)
        
        follow_exists = Follow.objects.filter(
            follower=request.user, 
            artist=artist
        ).exists()
        
        if follow_exists:
            Follow.objects.filter(follower=request.user, artist=artist).delete()
            followed = False
            message = f"You unfollowed {artist.name}"
        else:
            Follow.objects.create(follower=request.user, artist=artist)
            followed = True
            message = f"You are now following {artist.name}"
        
        followers_count = artist.followers.count()
        
        return JsonResponse({
            'success': True,
            'followed': followed,
            'followers_count': followers_count,
            'message': message
        })
        
    except Artist.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Artist not found'
        }, status=404)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'An error occurred: {str(e)}'
        }, status=500)

@login_required
def increment_play_count(request, song_id):
    """API endpoint to increment play count"""
    if request.method == 'POST':
        song = get_object_or_404(Song, id=song_id)
        song.plays += 1
        song.save()
        
        return JsonResponse({
            'success': True,
            'new_play_count': song.plays
        })
    
    return JsonResponse({'success': False})

def artists(request):
    """All artists page with trending and new sections"""
    artists_list = Artist.objects.all().annotate(
        total_songs_count=Count('songs', filter=Q(songs__is_approved=True)),
        total_plays_count=Coalesce(Sum('songs__plays', filter=Q(songs__is_approved=True)), 0),
        followers_count=Count('followers')
    ).order_by('-created_at')
    
    thirty_days_ago = timezone.now() - timedelta(days=30)
    new_artists = artists_list.filter(created_at__gte=thirty_days_ago)[:8]
    
    seven_days_ago = timezone.now() - timedelta(days=7)
    trending_artists = Artist.objects.all().annotate(
        recent_followers=Count(
            'followers', 
            filter=Q(followers__followed_at__gte=seven_days_ago)
        ),
        total_followers_count=Count('followers'),
        total_songs_count=Count('songs', filter=Q(songs__is_approved=True))
    ).filter(recent_followers__gt=0).order_by('-recent_followers', '-total_followers_count')[:8]
    
    context = {
        'artists': artists_list,
        'new_artists': new_artists,
        'trending_artists': trending_artists,
        'title': 'All Artists'
    }
    return render(request, 'artists/artists.html', context)
def trending_artists(request):
    """Trending artists page with enhanced metrics"""
    seven_days_ago = timezone.now() - timedelta(days=7)
    
    trending_artists_list = Artist.objects.verified().annotate(
        weekly_plays=Coalesce(Sum(
            'songs__plays',
            filter=Q(songs__upload_date__gte=seven_days_ago, songs__is_approved=True)
        ), 0),
        weekly_followers=Count(
            'followers',
            filter=Q(followers__followed_at__gte=seven_days_ago)
        ),
        total_followers_count=Count('followers'),
        total_songs_count=Count('songs', filter=Q(songs__is_approved=True))
    ).filter(Q(weekly_plays__gt=0) | Q(weekly_followers__gt=0)).order_by('-weekly_plays', '-weekly_followers')
    
    context = {
        'artists': trending_artists_list,
        'title': 'Trending Artists'
    }
    return render(request, 'artists/artists.html', context)

def artist_detail(request, artist_id):
    """Artist profile page"""
    artist = get_object_or_404(Artist, id=artist_id)
    
    if request.user.is_authenticated and hasattr(request.user, 'artist_profile') and request.user.artist_profile == artist:
        songs = Song.objects.filter(artist=artist).order_by('-upload_date')
    else:
        songs = Song.objects.filter(artist=artist, is_approved=True).order_by('-upload_date')
    
    for song in songs:
        song.is_liked = False
        if request.user.is_authenticated:
            song.is_liked = Like.objects.filter(user=request.user, song=song).exists()
    
    is_following = False
    if request.user.is_authenticated:
        is_following = Follow.objects.filter(follower=request.user, artist=artist).exists()
    
    approved_songs = songs.filter(is_approved=True)
    total_plays = approved_songs.aggregate(total=Sum('plays'))['total'] or 0
    total_downloads = approved_songs.aggregate(total=Sum('downloads'))['total'] or 0
    total_likes = Like.objects.filter(song__in=approved_songs).count()
    
    context = {
        'artist': artist,
        'songs': songs,
        'is_following': is_following,
        'songs_count': approved_songs.count(),
        'total_plays': total_plays,
        'total_downloads': total_downloads,
        'total_likes': total_likes,
        'followers_count': artist.followers.count(),
    }
    return render(request, 'artists/artist_detail.html', context)

@login_required
def artist_dashboard(request):
    """Artist dashboard with earnings calculation"""
    try:
        artist = request.user.artist_profile
    except Artist.DoesNotExist:
        messages.error(request, "You need to be an artist to access the dashboard.")
        return redirect('home')

    # Get artist stats for approved songs only
    approved_songs = artist.songs.filter(is_approved=True)
    total_plays = approved_songs.aggregate(total=Sum('plays'))['total'] or 0
    total_downloads = approved_songs.aggregate(total=Sum('downloads'))['total'] or 0
    total_likes = Like.objects.filter(song__in=approved_songs).count()
    total_followers = Follow.objects.filter(artist=artist).count()

    # Calculate earnings using the defined rates
    stream_earnings = total_plays * STREAM_RATE
    download_earnings = total_downloads * DOWNLOAD_RATE
    total_earnings = stream_earnings + download_earnings
    available_balance = total_earnings

    # Get recent activity
    seven_days_ago = timezone.now() - timedelta(days=7)
    recent_plays = approved_songs.aggregate(
        recent=Sum('plays', filter=Q(upload_date__gte=seven_days_ago))
    )['recent'] or 0
    
    recent_followers = Follow.objects.filter(
        artist=artist, 
        followed_at__gte=seven_days_ago
    ).count()

    # Get songs with earnings calculation
    recent_songs = artist.songs.all().order_by('-upload_date')[:6]
    top_songs = approved_songs.order_by('-plays')[:5]

    # Calculate earnings for each song
    for song in recent_songs:
        song.earnings = (song.plays * STREAM_RATE) + (song.downloads * DOWNLOAD_RATE)
    
    for song in top_songs:
        song.earnings = (song.plays * STREAM_RATE) + (song.downloads * DOWNLOAD_RATE)

    context = {
        'artist': artist,
        'total_plays': total_plays,
        'total_downloads': total_downloads,
        'total_likes': total_likes,
        'total_followers': total_followers,
        'total_earnings': total_earnings,
        'stream_earnings': stream_earnings,
        'download_earnings': download_earnings,
        'available_balance': available_balance,
        'recent_plays': recent_plays,
        'recent_followers': recent_followers,
        'recent_songs': recent_songs,
        'top_songs': top_songs,
        'genres': Genre.objects.all(),
    }
    return render(request, 'artists/artist_dashboard.html', context)
@login_required
def upload_music(request):
    """Song upload for artists with featured artist support"""
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
                
                # Handle featured artist selection
                artist_selection = request.POST.get('artist_selection', 'default')
                featured_artist_name = request.POST.get('featured_artist_name', '').strip()
                collaborating_artists = request.POST.get('collaborating_artists', '').strip()
                collaboration_type = request.POST.get('collaboration_type', '')
                
                # Set the display artist based on selection
                if artist_selection == 'featured' and featured_artist_name:
                    song.display_artist = featured_artist_name
                    song.is_featured = True
                    song.collaboration_type = collaboration_type
                    
                    # Store collaborating artists
                    if collaborating_artists:
                        song.collaborating_artists = collaborating_artists
                else:
                    # Use the artist's own name
                    song.display_artist = artist_profile.name
                    song.is_featured = False
                
                # Audio file validation
                if 'audio_file' in request.FILES:
                    audio_file = request.FILES['audio_file']
                    
                    max_size = 20 * 1024 * 1024  # 20MB
                    if audio_file.size > max_size:
                        messages.error(request, f"Audio file must be less than 20MB (current: {audio_file.size // (1024*1024)}MB)")
                        return render(request, 'artists/upload_music.html', {
                            'form': form,
                            'genres': Genre.objects.all(),
                            'max_file_size': 20,
                            'allowed_formats': ['MP3', 'WAV', 'OGG', 'M4A', 'FLAC']
                        })
                    
                    allowed_extensions = ['mp3', 'wav', 'ogg', 'm4a', 'flac']
                    file_extension = audio_file.name.split('.')[-1].lower()
                    if file_extension not in allowed_extensions:
                        messages.error(request, f"File type '{file_extension}' not supported. Allowed: {', '.join(allowed_extensions)}")
                        return render(request, 'artists/upload_music.html', {
                            'form': form,
                            'genres': Genre.objects.all(),
                            'max_file_size': 20,
                            'allowed_formats': ['MP3', 'WAV', 'OGG', 'M4A', 'FLAC']
                        })
                
                # Cover image validation (optional)
                if 'cover_image' in request.FILES:
                    cover_image = request.FILES['cover_image']
                    max_image_size = 10 * 1024 * 1024  # 10MB
                    if cover_image.size > max_image_size:
                        messages.error(request, f"Cover image must be less than 10MB (current: {cover_image.size // (1024*1024)}MB)")
                        return render(request, 'artists/upload_music.html', {
                            'form': form,
                            'genres': Genre.objects.all(),
                            'max_file_size': 20,
                            'allowed_formats': ['MP3', 'WAV', 'OGG', 'M4A', 'FLAC']
                        })
                    
                    allowed_image_extensions = ['jpg', 'jpeg', 'png', 'webp']
                    image_extension = cover_image.name.split('.')[-1].lower()
                    if image_extension not in allowed_image_extensions:
                        messages.error(request, f"Image type '{image_extension}' not supported. Allowed: {', '.join(allowed_image_extensions)}")
                        return render(request, 'artists/upload_music.html', {
                            'form': form,
                            'genres': Genre.objects.all(),
                            'max_file_size': 20,
                            'allowed_formats': ['MP3', 'WAV', 'OGG', 'M4A', 'FLAC']
                        })
                
                song.save()
                form.save_m2m()
                
                # Success message based on artist selection
                if song.is_featured:
                    messages.success(request, 
                        f"Your song '{song.title}' has been uploaded as '{song.display_artist}' and is pending review!"
                    )
                else:
                    messages.success(request, 
                        f"Your song '{song.title}' has been uploaded successfully and is pending review!"
                    )
                
                return redirect('artist_dashboard')
                
            except Exception as e:
                logger.error(f"Error saving song: {str(e)}")
                messages.error(request, "An error occurred while uploading your song. Please try again.")
        else:
            # Enhanced error handling
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    field_name = field.replace('_', ' ').title()
                    error_messages.append(f"{field_name}: {error}")
            
            if error_messages:
                messages.error(request, "Please correct the following errors: " + "; ".join(error_messages))
    else:
        form = SongUploadForm()
    
    context = {
        'form': form,
        'genres': Genre.objects.all(),
        'max_file_size': 20,
        'allowed_formats': ['MP3', 'WAV', 'OGG', 'M4A', 'FLAC'],
        'artist': artist_profile
    }
    return render(request, 'artists/upload_music.html', context)

@require_POST
@login_required
def follow_artist(request, artist_id):
    """API endpoint to follow/unfollow an artist"""
    try:
        artist = get_object_or_404(Artist, id=artist_id, is_verified=True)
        
        if hasattr(request.user, 'artist_profile') and request.user.artist_profile == artist:
            return JsonResponse({
                'success': False,
                'error': 'You cannot follow yourself'
            }, status=400)
        
        follow_exists = Follow.objects.filter(follower=request.user, artist=artist).exists()
        
        if follow_exists:
            Follow.objects.filter(follower=request.user, artist=artist).delete()
            followed = False
            message = f"You unfollowed {artist.name}"
        else:
            Follow.objects.create(follower=request.user, artist=artist)
            followed = True
            message = f"You are now following {artist.name}"
        
        followers_count = artist.followers.count()
        
        return JsonResponse({
            'success': True,
            'followed': followed,
            'followers_count': followers_count,
            'message': message
        })
        
    except Artist.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Artist not found'
        }, status=404)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'An error occurred: {str(e)}'
        }, status=500)

# Placeholder views for future implementation
def artist_analytics(request, artist_id):
    """Artist analytics page - placeholder"""
    context = {
        'page_title': 'Artist Analytics',
        'artist_id': artist_id,
    }
    return render(request, 'artists/placeholder_page.html', context)

@login_required
def edit_artist_profile(request):
    """Edit artist profile - placeholder"""
    context = {
        'page_title': 'Edit Artist Profile',
        'message': 'This feature will be available soon!',
    }
    return render(request, 'artists/placeholder_page.html', context)

@login_required
def earnings_details(request):
    """Artist earnings details - placeholder"""
    context = {
        'page_title': 'Earnings Details',
        'message': 'Detailed earnings analytics coming soon!',
    }
    return render(request, 'artists/placeholder_page.html', context)

@login_required
def activity_log(request):
    """Artist activity log - placeholder"""
    context = {
        'page_title': 'Activity Log',
        'message': 'Activity tracking will be available soon!',
    }
    return render(request, 'artists/placeholder_page.html', context)

@login_required
def my_uploads(request):
    """My uploads page - placeholder"""
    context = {
        'page_title': 'My Uploads',
        'message': 'Manage all your uploaded songs here.',
    }
    return render(request, 'artists/placeholder_page.html', context)
