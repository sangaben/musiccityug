# library/views.py - COMPLETE FIXED VERSION
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt

from .models import Playlist, Like
from music.models import Song, SongPlay
from artists.models import Artist

@login_required
def library(request):
    """User library with liked songs and playlists"""
    user_profile = request.user.userprofile
    liked_songs = user_profile.liked_songs.all()
    playlists = Playlist.objects.filter(user=request.user)
    
    context = {
        'liked_songs': liked_songs,
        'playlists': playlists,
    }
    return render(request, 'library/library.html', context)

@login_required
def playlists(request):
    """User playlists management"""
    playlists = Playlist.objects.filter(user=request.user)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Playlist.objects.create(name=name, user=request.user)
            messages.success(request, 'Playlist created successfully!')
            return redirect('playlists')
    
    context = {
        'playlists': playlists,
    }
    return render(request, 'library/playlists.html', context)

@login_required
def playlist_detail(request, playlist_id):
    """Individual playlist detail"""
    playlist = get_object_or_404(Playlist, id=playlist_id, user=request.user)
    
    if request.method == 'POST':
        song_id = request.POST.get('song_id')
        if song_id:
            song = get_object_or_404(Song, id=song_id)
            playlist.songs.add(song)
            messages.success(request, 'Song added to playlist!')
    
    context = {
        'playlist': playlist,
    }
    return render(request, 'library/playlist_detail.html', context)

@login_required
def liked_songs(request):
    """Display all songs liked by the current user"""
    liked_songs = Song.objects.filter(like__user=request.user).distinct()
    
    context = {
        'liked_songs': liked_songs,
        'title': 'Liked Songs',
        'section': 'library'
    }
    return render(request, 'library/liked_songs.html', context)

@login_required
def recently_played(request):
    """Display recently played songs for the current user"""
    try:
        recent_plays = SongPlay.objects.filter(user=request.user).order_by('-played_at')[:50]
        
        # Extract songs from play history (remove duplicates, keep most recent)
        seen_songs = set()
        recent_songs = []
        
        for play in recent_plays:
            if play.song.id not in seen_songs:
                recent_songs.append(play.song)
                seen_songs.add(play.song.id)
        
        # Add liked status to each song for template
        for song in recent_songs:
            song.is_liked = Like.objects.filter(user=request.user, song=song).exists()
            
        context = {
            'recent_songs': recent_songs,
            'title': 'Recently Played',
            'section': 'library'
        }
        return render(request, 'library/recently_played.html', context)
    except Exception as e:
        recent_songs = Song.objects.filter(is_approved=True).order_by('-upload_date')[:20]
        
        for song in recent_songs:
            song.is_liked = Like.objects.filter(user=request.user, song=song).exists()
            
        context = {
            'recent_songs': recent_songs,
            'title': 'Recently Played',
            'section': 'library'
        }
        return render(request, 'library/recently_played.html', context)

@login_required
def like_song(request, song_id):
    """Like or unlike a song"""
    song = get_object_or_404(Song, id=song_id)
    
    # Check if user already liked the song
    like_exists = Like.objects.filter(user=request.user, song=song).exists()
    
    if like_exists:
        # Unlike the song
        Like.objects.filter(user=request.user, song=song).delete()
        messages.success(request, f'Removed {song.title} from liked songs')
    else:
        # Like the song
        Like.objects.create(user=request.user, song=song)
        messages.success(request, f'Added {song.title} to liked songs')
    
    # Redirect back to the previous page
    return redirect(request.META.get('HTTP_REFERER', 'home'))

@login_required
def remove_from_playlist(request, playlist_id, song_id):
    """Remove song from playlist"""
    playlist = get_object_or_404(Playlist, id=playlist_id, user=request.user)
    song = get_object_or_404(Song, id=song_id)
    
    playlist.songs.remove(song)
    messages.success(request, 'Song removed from playlist!')
    return redirect('playlist_detail', playlist_id=playlist_id)

@login_required
def delete_playlist(request, playlist_id):
    """Delete playlist"""
    playlist = get_object_or_404(Playlist, id=playlist_id, user=request.user)
    playlist.delete()
    messages.success(request, 'Playlist deleted!')
    return redirect('playlists')

@csrf_exempt
@login_required
def add_to_playlist(request, song_id):
    """Add song to playlist"""
    if request.method == 'POST':
        song = get_object_or_404(Song, id=song_id)
        playlist_id = request.POST.get('playlist_id')
        
        if playlist_id:
            playlist = get_object_or_404(Playlist, id=playlist_id, user=request.user)
            playlist.songs.add(song)
            return JsonResponse({'success': True})
        
    return JsonResponse({'success': False})