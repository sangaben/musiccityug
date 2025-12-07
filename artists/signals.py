# artists/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import create_artist_profile

@receiver(post_save, sender='music.Song')
def auto_create_artist_profile_on_song_upload(sender, instance, created, **kwargs):
    """
    Automatically create artist profile when a user uploads their first song
    """
    if created:
        try:
            user = instance.artist.user
            print(f"Processing song upload for user: {user.username}")
            
            # Check if artist profile already exists
            if not hasattr(user, 'artist_profile'):
                print(f"Creating artist profile for {user.username}")
                
                # Create artist profile using the utility function
                artist_profile, created = create_artist_profile(
                    user,
                    name=user.get_full_name() or user.username,
                    bio=f"Artist on Sangabiz - {instance.genre.name} artist" if instance.genre else "Artist on Sangabiz",
                    genre=instance.genre
                )
                
                if created:
                    print(f"✅ Auto-created artist profile for {user.username}")
                else:
                    print(f"ℹ️ Updated existing artist profile for {user.username}")
            else:
                print(f"ℹ️ Artist profile already exists for {user.username}")
                    
        except Exception as e:
            print(f"❌ Error auto-creating artist profile: {e}")

@receiver(post_save, sender='accounts.UserProfile')
def sync_artist_profile_with_user_type(sender, instance, created, **kwargs):
    """
    Sync artist profile when user type changes to 'artist'
    """
    if not created and instance.user_type == 'artist':
        # Ensure artist profile exists when user becomes artist
        if not hasattr(instance.user, 'artist_profile'):
            print(f"Creating artist profile for {instance.user.username} (user type changed to artist)")
            create_artist_profile(
                instance.user,
                name=instance.user.get_full_name() or instance.user.username,
                bio=instance.bio or "Artist on Sangabiz"
            )