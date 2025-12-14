# artists/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class ArtistManager(models.Manager):
    def verified(self):
        return self.filter(is_verified=True)

class Artist(models.Model):
    # Completely remove the user field if you want artists independent
    name = models.CharField(max_length=200)
    bio = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='artists/', blank=True, null=True)
    genre = models.ForeignKey('music.Genre', on_delete=models.SET_NULL, null=True, blank=True)
    website = models.URLField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)  # Add email for contact
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = ArtistManager()
    
    class Meta:
        app_label = 'artists'
    
    def __str__(self):
        return self.name

class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='followers')
    followed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['follower', 'artist']
        app_label = 'artists'
