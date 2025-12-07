# accounts/models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from datetime import timedelta

class UserProfile(models.Model):
    USER_TYPE_CHOICES = [
        ('listener', 'Listener'),
        ('artist', 'Artist'),
    ]
    
    PREMIUM_PLAN_CHOICES = [
        ('free', 'Free'),
        ('premium', 'Premium'),
        ('premium_plus', 'Premium Plus'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='listener')
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # ADD THIS: Liked songs relationship
    liked_songs = models.ManyToManyField(
        'music.Song', 
        related_name='liked_by_users', 
        blank=True,
        through='LikedSong'
    )
    
    # Premium subscription fields
    premium_plan = models.CharField(
        max_length=20, 
        choices=PREMIUM_PLAN_CHOICES, 
        default='free'
    )
    premium_since = models.DateTimeField(blank=True, null=True)
    premium_expires = models.DateTimeField(blank=True, null=True)
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_subscription_id = models.CharField(max_length=255, blank=True, null=True)
    
    # Premium features usage tracking
    offline_downloads_used = models.PositiveIntegerField(default=0)
    max_offline_downloads = models.PositiveIntegerField(default=0)  # 0 = unlimited for premium
    
    def __str__(self):
        return self.user.username
    
    @property
    def is_artist(self):
        return self.user_type == 'artist'
    
    @property
    def is_premium(self):
        """Check if user has an active premium subscription"""
        return self.premium_plan in ['premium', 'premium_plus'] and self.is_premium_active
    
    @property
    def is_premium_active(self):
        """Check if premium subscription is currently active"""
        if self.premium_plan == 'free':
            return False
        if not self.premium_expires:
            return True  # Lifetime subscription
        return timezone.now() < self.premium_expires
    
    @property
    def days_until_expiry(self):
        """Days until premium expires"""
        if not self.is_premium_active or not self.premium_expires:
            return 0
        delta = self.premium_expires - timezone.now()
        return max(0, delta.days)
    
    @property
    def artist_profile(self):
        if self.is_artist:
            try:
                return self.user.artist_profile
            except ObjectDoesNotExist:
                # Auto-correct if artist profile doesn't exist
                self.user_type = 'listener'
                self.save()
                return None
        return None
    
    def upgrade_to_premium(self, plan_type='premium', duration_days=30):
        """Upgrade user to premium plan"""
        self.premium_plan = plan_type
        self.premium_since = timezone.now()
        self.premium_expires = timezone.now() + timedelta(days=duration_days)
        
        # Set download limits based on plan
        if plan_type == 'premium':
            self.max_offline_downloads = 100  # 100 songs for premium
        elif plan_type == 'premium_plus':
            self.max_offline_downloads = 0  # Unlimited for premium plus
        
        self.save()
    
    def downgrade_to_free(self):
        """Downgrade user to free plan"""
        self.premium_plan = 'free'
        self.premium_expires = None
        self.max_offline_downloads = 0
        self.offline_downloads_used = 0
        self.save()
    
    def can_download_offline(self):
        """Check if user can download more songs offline"""
        if not self.is_premium_active:
            return False
        if self.max_offline_downloads == 0:  # Unlimited
            return True
        return self.offline_downloads_used < self.max_offline_downloads
    
    def record_offline_download(self):
        """Record an offline download"""
        if self.can_download_offline():
            self.offline_downloads_used += 1
            self.save()
            return True
        return False
    
    def get_premium_plan_display_name(self):
        """Get formatted premium plan name"""
        return dict(self.PREMIUM_PLAN_CHOICES).get(self.premium_plan, 'Free')

    class Meta:
        app_label = 'accounts'


# Add this intermediate model for liked songs with additional data
class LikedSong(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    song = models.ForeignKey('music.Song', on_delete=models.CASCADE)
    liked_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user_profile', 'song']
        ordering = ['-liked_at']
        app_label = 'accounts'


# FIXED: Simplified signal handler
@receiver(post_save, sender=User)
def manage_user_profile(sender, instance, created, **kwargs):
    """
    Single signal handler to manage UserProfile creation and updates
    """
    if created:
        # Only create profile if it doesn't exist
        UserProfile.objects.get_or_create(user=instance)
    else:
        # Only save if profile exists, don't create on updates
        try:
            instance.userprofile.save()
        except UserProfile.DoesNotExist:
            # If profile doesn't exist on update, create it
            UserProfile.objects.create(user=instance)