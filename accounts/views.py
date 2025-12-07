# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction

from music.models import Genre, SongPlay
from artists.models import Artist
from library.models import Playlist
from .models import UserProfile


def login_view(request):
    """User login view"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {username}!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'accounts/login.html')




def signup(request):
    if request.method == 'POST':
        # Get form data
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        is_artist = request.POST.get('is_artist') == 'on'
        artist_name = request.POST.get('artist_name', '')
        bio = request.POST.get('bio', '')
        genre_id = request.POST.get('genre')
        website = request.POST.get('website', '')
        terms = request.POST.get('terms')
        artist_image = request.FILES.get('artist_image')  # Get uploaded image

        # Basic validation
        errors = []
        
        if not username or not email or not password1:
            errors.append('All required fields must be filled.')
        
        if len(password1) < 8:
            errors.append('Password must be at least 8 characters long.')
        
        if password1 != password2:
            errors.append('Passwords do not match.')
        
        if User.objects.filter(username=username).exists():
            errors.append('Username already exists.')
        
        if User.objects.filter(email=email).exists():
            errors.append('Email already exists.')
        
        if not terms:
            errors.append('You must agree to the Terms of Service.')
        
        # Artist-specific validation
        if is_artist:
            if not artist_name:
                errors.append('Artist name is required when signing up as an artist.')
            elif Artist.objects.filter(name=artist_name).exists():
                errors.append('An artist with this name already exists.')
            
            # Validate image if provided
            if artist_image:
                if artist_image.size > 5 * 1024 * 1024:  # 5MB limit
                    errors.append('Image size must be less than 5MB.')
                if not artist_image.content_type.startswith('image/'):
                    errors.append('Please upload a valid image file.')

        if errors:
            for error in errors:
                messages.error(request, error)
            
            return render(request, 'accounts/signup.html', {
                'genres': Genre.objects.all(),
                'username': username,
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'artist_name': artist_name,
                'bio': bio,
                'website': website,
                'is_artist': is_artist,
            })
        
        try:
            # Use transaction to ensure data consistency
            with transaction.atomic():
                # Create user
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password1,
                    first_name=first_name,
                    last_name=last_name
                )
                
                # Create UserProfile
                user_type = 'artist' if is_artist else 'listener'
                user_profile = UserProfile.objects.create(
                    user=user,
                    user_type=user_type
                )
                
                # Create artist profile if needed
                if is_artist:
                    artist_data = {
                        'user': user,
                        'name': artist_name,
                        'bio': bio,
                        'website': website if website else None,
                    }
                    
                    # Add image if provided
                    if artist_image:
                        artist_data['image'] = artist_image
                    
                    # Add genre if provided and exists
                    if genre_id:
                        try:
                            genre = Genre.objects.get(id=genre_id)
                            artist_data['genre'] = genre
                        except Genre.DoesNotExist:
                            # Continue without genre if it doesn't exist
                            pass
                    
                    Artist.objects.create(**artist_data)
                    messages.success(request, 'Artist account created successfully! Welcome to Sangabiz!')
                else:
                    messages.success(request, 'Account created successfully! Welcome to Sangabiz!')
                
                # Login user and redirect
                login(request, user)
                
                # Redirect based on user type
                if is_artist:
                    return redirect('artist_dashboard')
                else:
                    return redirect('home')
                
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
            # Log the error for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Signup error: {str(e)}")
            
            # Return with preserved data
            return render(request, 'accounts/signup.html', {
                'genres': Genre.objects.all(),
                'username': username,
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'artist_name': artist_name,
                'bio': bio,
                'website': website,
                'is_artist': is_artist,
            })
    
    # GET request - show empty form with genres
    return render(request, 'accounts/signup.html', {
        'genres': Genre.objects.all()
    })

def logout_view(request):
    """User logout view"""
    logout(request)
    messages.info(request, 'You have been successfully logged out.')
    return redirect('home')


@login_required
def profile_view(request):
    """User profile page"""
    user_profile = request.user.userprofile
    
    # Get user stats
    liked_songs_count = user_profile.liked_songs.count()
    playlists_count = Playlist.objects.filter(user=request.user).count()
    recent_plays = SongPlay.objects.filter(user=request.user).select_related('song').order_by('-played_at')[:10]
    
    context = {
        'user_profile': user_profile,
        'liked_songs_count': liked_songs_count,
        'playlists_count': playlists_count,
        'recent_plays': recent_plays,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def settings_view(request):
    """User settings page"""
    user_profile = request.user.userprofile
    
    if request.method == 'POST':
        # Handle settings updates
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        bio = request.POST.get('bio')
        location = request.POST.get('location')
        website = request.POST.get('website')
        
        # Update user
        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.save()
        
        # Update profile
        user_profile.bio = bio
        user_profile.location = location
        user_profile.website = website
        user_profile.save()
        
        messages.success(request, 'Settings updated successfully!')
        return redirect('settings')
    
    context = {
        'user_profile': user_profile,
    }
    return render(request, 'accounts/settings.html', context)