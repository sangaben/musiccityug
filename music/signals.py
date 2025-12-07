# music/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Song

@receiver(post_save, sender=Song)
def update_artist_profile(sender, instance, created, **kwargs):
    """
    Ensure artist profile exists when a song is uploaded
    """
    if created:
        try:
            user = instance.artist.user
            # This will trigger the artist profile creation if it doesn't exist
            if not hasattr(user, 'artist_profile'):
                from artists.models import create_artist_profile
                create_artist_profile(
                    user,
                    name=user.get_full_name() or user.username,
                    bio=f"Artist on Sangabiz - {instance.genre.name} artist",
                    genre=instance.genre
                )
        except Exception as e:
            print(f"Error in song post_save signal: {e}")