# artists/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class ArtistManager(models.Manager):
    def verified(self):
        return self.filter(is_verified=True)
    
    def with_stats(self):
        return self.annotate(
            total_songs=models.Count('songs'),
            total_plays=models.Sum('songs__plays'),
            total_downloads=models.Sum('songs__downloads')
        )
    
    def active_artists(self):
        """Artists who have at least one approved song"""
        return self.filter(songs__is_approved=True).distinct()

class Artist(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='artist_profile'
    )
    name = models.CharField(max_length=200)
    bio = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='artists/', blank=True, null=True)
    genre = models.ForeignKey('music.Genre', on_delete=models.SET_NULL, null=True, blank=True)
    website = models.URLField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = ArtistManager()
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user'], name='unique_artist_user')
        ]
    
    def __str__(self):
        return self.name
    
    @property
    def total_plays(self):
        return sum(song.plays for song in self.songs.all())
    
    @property
    def total_downloads(self):
        return sum(song.downloads for song in self.songs.all())
    
    @property
    def total_songs(self):
        return self.songs.count()
    
    @property
    def approved_songs_count(self):
        return self.songs.filter(is_approved=True).count()
    
    @property
    def is_new_artist(self):
        """Check if artist was created in the last 30 days"""
        return (timezone.now() - self.created_at).days <= 30
    
    @property
    def is_active(self):
        """Check if artist has approved songs"""
        return self.songs.filter(is_approved=True).exists()
    
    @property
    def recent_songs(self):
        """Get recent songs (last 30 days)"""
        thirty_days_ago = timezone.now() - timedelta(days=30)
        return self.songs.filter(upload_date__gte=thirty_days_ago, is_approved=True)

class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='followers')
    followed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['follower', 'artist']
        ordering = ['-followed_at']

# ===== UTILITY FUNCTIONS =====
def create_artist_profile(user, **kwargs):
    """
    Safely create an artist profile for a user
    Returns (artist, created) tuple
    """
    try:
        # Check if artist profile already exists
        if hasattr(user, 'artist_profile'):
            artist = user.artist_profile
            # Update existing artist with new data
            for key, value in kwargs.items():
                if hasattr(artist, key):
                    setattr(artist, key, value)
            artist.save()
            return artist, False
        else:
            # Create new artist profile
            artist = Artist.objects.create(user=user, **kwargs)
            # Update user profile
            from accounts.models import UserProfile
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.user_type = 'artist'
            profile.save()
            return artist, True
    except Exception as e:
        print(f"❌ Error creating artist profile: {e}")
        return None, False

def get_or_create_artist_for_user(user, **kwargs):
    """
    Get existing artist profile or create one for user
    This ensures every user who uploads songs becomes an artist automatically
    """
    try:
        if hasattr(user, 'artist_profile'):
            return user.artist_profile, False
        else:
            artist = Artist.objects.create(user=user, **kwargs)
            # Update user profile type
            from accounts.models import UserProfile
            user_profile, created = UserProfile.objects.get_or_create(user=user)
            user_profile.user_type = 'artist'
            user_profile.save()
            return artist, True
    except Exception as e:
        print(f"Error in get_or_create_artist_for_user: {e}")
        return None, False

# ===== MODEL METHODS FOR AUTO-ARTIST SYSTEM =====
def user_has_artist_access(user):
    """Check if user has access to artist features"""
    return (user.is_authenticated and 
            hasattr(user, 'userprofile') and 
            user.userprofile.is_artist)

def get_artists_with_songs():
    """Get all artists who have at least one approved song"""
    return Artist.objects.filter(songs__is_approved=True).distinct()

def get_trending_artists(days=7):
    """Get trending artists based on recent plays"""
    date_threshold = timezone.now() - timedelta(days=days)
    return Artist.objects.filter(
        songs__songplay__played_at__gte=date_threshold
    ).annotate(
        recent_plays=models.Count('songs__songplay')
    ).order_by('-recent_plays')

def get_user_audio_quality(user):
    """Get appropriate audio quality for user based on subscription"""
    if not user.is_authenticated or not hasattr(user, 'userprofile'):
        return 'standard'
    
    profile = user.userprofile
    if profile.premium_plan == 'premium_plus':
        return 'ultra'
    elif profile.premium_plan == 'premium':
        return 'high'
    else:
        return 'standard'