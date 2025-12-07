from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta

from music.models import Song, SongPlay, SongDownload
from artists.models import Artist

@login_required
def song_analytics(request, song_id):
    """Song analytics for artist"""
    song = get_object_or_404(Song, id=song_id)
    
    # Check if user owns the song
    if not request.user.userprofile.is_artist or song.artist.user != request.user:
        messages.error(request, "You don't have permission to view these analytics.")
        return redirect('my_uploads')
    
    # Get play history (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_plays = SongPlay.objects.filter(song=song, played_at__gte=thirty_days_ago)
    
    # Get download history
    recent_downloads = SongDownload.objects.filter(song=song, downloaded_at__gte=thirty_days_ago)
    
    context = {
        'song': song,
        'recent_plays': recent_plays,
        'recent_downloads': recent_downloads,
        'total_plays': song.plays,
        'total_downloads': song.downloads,
    }
    return render(request, 'analytics/song_analytics.html', context)

@login_required
def top_songs(request):
    """Top songs analytics"""
    # Get top played songs
    top_played = Song.objects.filter(is_approved=True).order_by('-plays')[:10]
    
    # Get top downloaded songs
    top_downloaded = Song.objects.filter(is_approved=True).order_by('-downloads')[:10]
    
    context = {
        'top_played': top_played,
        'top_downloaded': top_downloaded,
    }
    return render(request, 'analytics/top_songs.html', context)

def get_song_stats(request, song_id):
    """Get current song statistics"""
    song = get_object_or_404(Song, id=song_id)
    return JsonResponse({
        'plays': song.plays,
        'downloads': song.downloads
    })