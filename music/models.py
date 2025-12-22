# music/models.py - COMPLETE FIXED VERSION
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator, MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import timedelta

from django.urls import reverse

class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)
    color = models.CharField(max_length=7, default='#6c5ce7')  # Hex color
    description = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['name']
        app_label = 'music'
    
    def __str__(self):
        return self.name

class Song(models.Model):
    AUDIO_QUALITY_CHOICES = [
        ('standard', 'Standard'),
        ('high', 'High (320kbps)'),
        ('ultra', 'Ultra HD (FLAC)'),
    ]
    
    title = models.CharField(max_length=200)
    artist = models.ForeignKey('artists.Artist', on_delete=models.CASCADE, related_name='songs')
    
    # Display artist name field
    display_artist_name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Optional: Artist name to display (different from linked artist)"
    )
    
    featured_artists = models.ManyToManyField(
        'artists.Artist',
        related_name='featured_songs',
        blank=True
    )
    
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True, blank=True, related_name='songs')
    audio_file = models.FileField(
        upload_to='songs/',
        validators=[FileExtensionValidator(allowed_extensions=['mp3', 'wav', 'ogg', 'm4a'])]
    )
    cover_image = models.ImageField(upload_to='covers/', blank=True, null=True)
    
    # Duration fields
    duration_minutes = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(59)],
        help_text="Minutes part of duration (0-59)"
    )
    duration_seconds = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(59)],
        help_text="Seconds part of duration (0-59)"
    )
    
    upload_date = models.DateTimeField(auto_now_add=True)
    plays = models.PositiveIntegerField(default=0)
    downloads = models.PositiveIntegerField(default=0)
    is_approved = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    is_premium_only = models.BooleanField(default=False, help_text="Only available to premium users")
    preview_duration = models.PositiveIntegerField(default=30, help_text="Preview duration in seconds for free users")
    audio_quality = models.CharField(max_length=20, choices=AUDIO_QUALITY_CHOICES, default='standard')
    lyrics = models.TextField(blank=True, null=True)
    bpm = models.PositiveIntegerField(blank=True, null=True, help_text="Beats per minute")
    release_year = models.PositiveIntegerField(blank=True, null=True)

    
    def get_absolute_url(self):
        """
        Returns the URL to the song's detail page.
        Make sure your URL pattern name matches 'song_detail' and expects song_id.
        """
        return reverse('song_detail', kwargs={'song_id': self.id})
    
    class Meta:
        ordering = ['-upload_date']
        indexes = [
            models.Index(fields=['-upload_date']),
            models.Index(fields=['is_approved', 'is_featured']),
        ]
        app_label = 'music'
    
    def __str__(self):
        # Use caching to prevent recursion
        if hasattr(self, '_str_cache'):
            return self._str_cache
            
        artist_name = self.get_display_artist_name()
        featured_count = self.featured_artists.count()
        
        if featured_count > 0:
            result = f"{self.title} - {artist_name} ft. {featured_count} artist(s)"
        else:
            result = f"{self.title} - {artist_name}"
            
        # Cache the result
        self._str_cache = result
        return result
    
    def get_display_artist_name(self):
        """
        Returns the display artist name if set, otherwise returns the linked artist's name.
        """
        if self.display_artist_name:
            return self.display_artist_name
        
        try:
            return str(self.artist)
        except Exception:
            return "Unknown Artist"
    
    @property
    def display_artist(self):
        """Property version of get_display_artist_name() for template access."""
        return self.get_display_artist_name()
    
    # Property to get total duration in seconds
    @property
    def duration(self):
        """Return total duration in seconds."""
        return (self.duration_minutes * 60) + self.duration_seconds
    
    @duration.setter
    def duration(self, seconds):
        """Set duration from total seconds."""
        self.duration_minutes = seconds // 60
        self.duration_seconds = seconds % 60
    
    @property
    def all_artists(self):
        """Return list of all artists on the track."""
        artists = [self.artist]
        artists.extend(list(self.featured_artists.all()))
        return artists
    
    @property
    def all_artists_display(self):
        """Return list of all artist display names on the track."""
        artists = [self.get_display_artist_name()]
        
        # For featured artists, you could also add display names if needed
        for featured in self.featured_artists.all():
            artists.append(str(featured))
        
        return artists
    
    def increment_plays(self):
        self.plays += 1
        self.save()
    
    def increment_downloads(self):
        self.downloads += 1
        self.save()
    
    @property
    def formatted_duration(self):
        """Return duration in MM:SS format."""
        return f"{self.duration_minutes:02d}:{self.duration_seconds:02d}"
    
    @property
    def is_recent(self):
        return (timezone.now() - self.upload_date).days <= 7
    
    @property
    def popularity_score(self):
        """Calculate a simple popularity score based on plays and downloads"""
        return self.plays + (self.downloads * 2)
    
    def can_be_accessed_by(self, user):
        """Check if user can access this song"""
        if not self.is_premium_only:
            return True
        if user.is_authenticated and hasattr(user, 'userprofile'):
            return user.userprofile.is_premium_active
        return False

class SongPlay(models.Model):
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name='play_history')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='song_plays')
    played_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    duration_played = models.PositiveIntegerField(default=0, help_text="Seconds played")
    
    # Device and session info
    user_agent = models.TextField(blank=True, null=True)
    session_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Premium analytics
    audio_quality = models.CharField(
        max_length=20, 
        choices=Song.AUDIO_QUALITY_CHOICES,
        default='standard'
    )
    
    # ADD THESE FIELDS
    is_anonymous = models.BooleanField(default=False, help_text="True if play is from anonymous user")
    
    class Meta:
        ordering = ['-played_at']
        indexes = [
            models.Index(fields=['-played_at']),
            models.Index(fields=['song', 'played_at']),
        ]
        app_label = 'music'
    
    def __str__(self):
        if self.user:
            return f"{self.song.title} played by {self.user.username}"
        else:
            return f"Anonymous played {self.song.title}"

class SongDownload(models.Model):
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name='download_history')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='song_downloads')
    downloaded_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    # Download details
    is_offline_download = models.BooleanField(default=False)
    audio_quality = models.CharField(
        max_length=20, 
        choices=Song.AUDIO_QUALITY_CHOICES,
        default='standard'
    )
    file_size = models.PositiveIntegerField(help_text="File size in bytes", null=True, blank=True)
    
    class Meta:
        ordering = ['-downloaded_at']
        indexes = [
            models.Index(fields=['-downloaded_at']),
            models.Index(fields=['song', 'downloaded_at']),
        ]
        app_label = 'music'
    
    def __str__(self):
        return f"{self.song.title} downloaded by {self.user.username if self.user else 'Anonymous'}"
