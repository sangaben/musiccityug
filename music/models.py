# music/models.py
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.utils import timezone
from datetime import timedelta

class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)
    color = models.CharField(max_length=7, default='#6c5ce7')  # Hex color
    description = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['name']
        app_label = 'music'  # Add this line
    
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
    
    # FIXED: Only ONE genre field
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True, blank=True, related_name='songs')
    
    audio_file = models.FileField(
        upload_to='songs/',
        validators=[FileExtensionValidator(allowed_extensions=['mp3', 'wav', 'ogg', 'm4a'])]
    )
    cover_image = models.ImageField(upload_to='covers/', blank=True, null=True)
    duration = models.PositiveIntegerField(help_text="Duration in seconds", default=0)
    upload_date = models.DateTimeField(auto_now_add=True)
    plays = models.PositiveIntegerField(default=0)
    downloads = models.PositiveIntegerField(default=0)
    
    # REMOVED: Duplicate genre field that was here
    
    is_approved = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    
    # Premium content fields
    is_premium_only = models.BooleanField(default=False, help_text="Only available to premium users")
    preview_duration = models.PositiveIntegerField(default=30, help_text="Preview duration in seconds for free users")
    audio_quality = models.CharField(max_length=20, choices=AUDIO_QUALITY_CHOICES, default='standard')
    
    # Metadata
    lyrics = models.TextField(blank=True, null=True)
    bpm = models.PositiveIntegerField(blank=True, null=True, help_text="Beats per minute")
    release_year = models.PositiveIntegerField(blank=True, null=True)
    
    class Meta:
        ordering = ['-upload_date']
        indexes = [
            models.Index(fields=['-upload_date']),
            models.Index(fields=['is_approved', 'is_featured']),
        ]
        app_label = 'music'  # Add this line
    
    def __str__(self):
        return f"{self.title} - {self.artist.name}"
    
    def increment_plays(self):
        self.plays += 1
        self.save()
    
    def increment_downloads(self):
        self.downloads += 1
        self.save()
    
    @property
    def formatted_duration(self):
        minutes = self.duration // 60
        seconds = self.duration % 60
        return f"{minutes}:{seconds:02d}"
    
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
# music/models.py - UPDATE THE SongPlay MODEL

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
        app_label = 'music'  # Add this line
    
    def __str__(self):
        return f"{self.song.title} downloaded by {self.user.username if self.user else 'Anonymous'}"

# Remove the duplicate Genre definition at the bottom
# The Genre class is already defined at the top