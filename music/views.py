# music/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse, FileResponse
from django.db.models import Q, Count, Sum, Avg, F
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.paginator import Paginator
from django.conf import settings
from django.db import transaction
from datetime import timedelta
import json
import os
import tempfile
import shutil
import re

from .models import Song, Genre, SongPlay, SongDownload
from .forms import SongUploadForm

# Utility function to get client IP
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

# ========== COMPLETE HELPER FUNCTIONS ==========
def create_branded_cover(song, logo_path, output_path):
    """Create branded cover art with ONLY MusicCityUg logo (replaces song cover)"""
    try:
        from PIL import Image, ImageDraw, ImageFont, ImageFilter
        
        print(f"🎨 Creating branded cover for: {song.title}")
        print(f"🏷️ Using logo: {logo_path}")
        
        # Create base image (600x600 for good quality)
        img = Image.new('RGB', (600, 600), color='#121212')
        draw = ImageDraw.Draw(img)
        
        # Add gradient background (dark to slightly lighter)
        for i in range(600):
            r = int(18 + (i / 600) * 30)
            g = int(18 + (i / 600) * 30)
            b = int(18 + (i / 600) * 30)
            draw.line([(0, i), (600, i)], fill=(r, g, b))
        
        # Add Sangabiz logo as the MAIN element
        if logo_path and os.path.exists(logo_path):
            try:
                print(f"🏷️ Loading logo: {logo_path}")
                logo = Image.open(logo_path)
                
                # Convert to RGBA if not already
                if logo.mode != 'RGBA':
                    logo = logo.convert('RGBA')
                
                # Resize logo to be large and centered (400x400)
                logo = logo.resize((400, 400), Image.Resampling.LANCZOS)
        
                
                # Apply slight blur to edges for smooth look
                mask = mask.filter(ImageFilter.GaussianBlur(2))
                
                # Paste logo in the center
                img.paste(logo, (100, 100), mask)
                
                # Add glow effect around logo
                for i in range(1, 5):
                    draw.ellipse([(100-i, 100-i), (500+i, 500+i)], 
                                outline='rgba(29, 185, 84, 0.2)', width=1)
                
                print("✅ Logo added as main cover element")
                
            except Exception as e:
                print(f"⚠️ Error loading logo: {e}")
                # Fallback: Create music note design
                draw.ellipse([(150, 150), (450, 450)], 
                           outline='#1DB954', width=10)
                try:
                    font = ImageFont.truetype("arial.ttf", 120)
                except:
                    font = ImageFont.load_default()
                draw.text((300, 300), "♪", fill='#1DB954', font=font, anchor="mm")
        else:
            print("⚠️ No logo found, creating default design")
            # Create default music note design
            draw.ellipse([(150, 150), (450, 450)], 
                       outline='#1DB954', width=10)
            try:
                font = ImageFont.truetype("arial.ttf", 120)
            except:
                font = ImageFont.load_default()
            draw.text((300, 300), "♪", fill='#1DB954', font=font, anchor="mm")
        
        # Add branding text at the bottom
        try:
            font_brand = ImageFont.truetype("arial.ttf", 28)
        except:
            font_brand = ImageFont.load_default()
        
        # Add "Downloaded from" text
        draw.text((300, 550), "Downloaded from", 
                 fill='#FFFFFF', font=font_brand, anchor="mm", stroke_width=1, stroke_fill='black')
        
        # Add "Sangabiz" in green
        draw.text((300, 580), "MusicCenterUg", 
                 fill='#1DB954', font=font_brand, anchor="mm", stroke_width=1, stroke_fill='black')
        
        # Add song info at the top
        try:
            font_info = ImageFont.truetype("arial.ttf", 20)
        except:
            font_info = ImageFont.load_default()
        
        # Song title (truncate if too long)
        title = song.title
        if len(title) > 25:
            title = title[:22] + "..."
        draw.text((300, 40), title, 
                 fill='white', font=font_info, anchor="mm", stroke_width=1, stroke_fill='black')
        
        # Artist name
        artist = song.artist.name
        if len(artist) > 25:
            artist = artist[:22] + "..."
        draw.text((300, 65), f"by {artist}", 
                 fill='#1DB954', font=font_info, anchor="mm", stroke_width=1, stroke_fill='black')
        
        # Save the image
        img.save(output_path, 'JPEG', quality=95)
        print(f"✅ Branded cover saved to: {output_path}")
        print(f"📏 Cover size: {os.path.getsize(output_path)} bytes")
        
    except Exception as e:
        print(f"❌ Error creating branded cover: {e}")
        import traceback
        traceback.print_exc()
        
        # Create ultra-simple fallback cover
        from PIL import Image, ImageDraw
        img = Image.new('RGB', (600, 600), color='#1DB954')
        draw = ImageDraw.Draw(img)
        draw.text((300, 250), "MusicCenterUg", 
                 fill='white', font=ImageFont.load_default(), anchor="mm")
        draw.text((300, 300), song.title[:20], 
                 fill='white', font=ImageFont.load_default(), anchor="mm")
        img.save(output_path, 'JPEG')
        print(f"⚠️ Created fallback cover: {output_path}")

def add_metadata_to_audio(audio_path, song, cover_path, logo_path):
    """Add metadata and branding to audio file"""
    try:
        print(f"🎵 Adding metadata to audio: {audio_path}")
        
        # Ensure the audio file exists
        if not os.path.exists(audio_path):
            print(f"❌ Audio file not found: {audio_path}")
            return False
        
        # Try using mutagen (for MP3 files)
        try:
            import mutagen
            from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB, TCON, TDRC, COMM, TPE2
            from mutagen.mp3 import MP3
            
            # Load audio file
            audio = MP3(audio_path, ID3=ID3)
            
            # Remove existing ID3 tags to start fresh
            try:
                audio.delete()
            except:
                pass
            
            # Create new ID3 tags if they don't exist
            if audio.tags is None:
                audio.add_tags()
            
            # Add basic metadata
            audio['TIT2'] = TIT2(encoding=3, text=[song.title])  # Title
            audio['TPE1'] = TPE1(encoding=3, text=[song.artist.name])  # Artist
            
            # Album/Artist (use artist name if no album)
            if hasattr(song, 'album') and song.album:
                audio['TALB'] = TALB(encoding=3, text=[song.album.name])
                audio['TPE2'] = TPE2(encoding=3, text=[song.artist.name])  # Album artist
            else:
                audio['TALB'] = TALB(encoding=3, text=[f"{song.artist.name} - Singles"])
                audio['TPE2'] = TPE2(encoding=3, text=[song.artist.name])
            
            # Genre
            audio['TCON'] = TCON(encoding=3, text=[song.genre.name])
            
            # Year/Date
            if song.upload_date:
                year = song.upload_date.strftime("%Y")
                audio['TDRC'] = TDRC(encoding=3, text=[year])
            
            # Add cover art if available
            if cover_path and os.path.exists(cover_path):
                try:
                    with open(cover_path, 'rb') as cover_file:
                        cover_data = cover_file.read()
                    
                    audio.tags.add(
                        APIC(
                            encoding=3,  # UTF-8
                            mime='image/jpeg',
                            type=3,  # Cover (front)
                            desc='Cover',
                            data=cover_data
                        )
                    )
                    print(f"✅ Added cover art: {cover_path}")
                except Exception as e:
                    print(f"⚠️ Error adding cover art: {e}")
            else:
                print("ℹ️ No cover art to add")
            
            # Add branding comment
            comment_text = f"Downloaded from MusicCityUg - Uganda's Music Hub\n{song.artist.name} - {song.title}"
            audio['COMM'] = COMM(encoding=3, lang='eng', desc='', text=[comment_text])
            
            # Save metadata
            audio.save(v2_version=3)  # Use ID3v2.3 for better compatibility
            print(f"✅ Metadata added successfully using mutagen")
            
            return True
            
        except ImportError:
            print("⚠️ mutagen not installed, trying eyed3")
            # Fallback to eyed3 if mutagen fails
            try:
                import eyed3
                
                audiofile = eyed3.load(audio_path)
                if audiofile.tag is None:
                    audiofile.initTag()
                
                # Set basic metadata
                audiofile.tag.title = song.title
                audiofile.tag.artist = song.artist.name
                audiofile.tag.album = f"{song.artist.name} - Singles"
                audiofile.tag.album_artist = song.artist.name
                audiofile.tag.genre = song.genre.name
                
                if song.upload_date:
                    audiofile.tag.year = song.upload_date.year
                
                # Add cover art
                if cover_path and os.path.exists(cover_path):
                    with open(cover_path, 'rb') as img_file:
                        audiofile.tag.images.set(3, img_file.read(), 'image/jpeg')
                
                # Add comment
                audiofile.tag.comments.set("Downloaded from MusicCityUg - Uganda's Music Hub\n")
                
                audiofile.tag.save()
                print(f"✅ Metadata added using eyed3")
                return True
                
            except ImportError:
                print("⚠️ eyed3 not installed, using simple metadata")
                # If both libraries fail, at least we tried
                return False
            except Exception as e:
                print(f"⚠️ Error with eyed3: {e}")
                return False
        
    except Exception as e:
        print(f"❌ Error adding metadata: {e}")
        import traceback
        traceback.print_exc()
        return False

# ========== CHECK PREMIUM STATUS ==========
def check_premium_access(request, song_id):
    """Check if user can download a song"""
    if request.method == 'GET':
        try:
            song = get_object_or_404(Song, id=song_id)
            
            can_access = song.can_be_accessed_by(request.user)
            
            return JsonResponse({
                'success': True,
                'song_id': song_id,
                'title': song.title,
                'is_premium': song.is_premium_only,
                'can_access': can_access,
                'is_authenticated': request.user.is_authenticated,
                'message': 'Premium song - login required' if song.is_premium_only and not can_access else 'Download available'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid method'})

def home(request):
    """Home page with featured content and news"""
    print("🔄 Home view called")
    
    try:
        # Get featured songs (most played + recently uploaded)
        featured_songs = Song.objects.filter(
            is_approved=True
        ).select_related('artist', 'genre').order_by('-plays', '-upload_date')[:12]
        print(f"🎵 Found {len(featured_songs)} featured songs")

        # Most played songs (for top charts)
        most_played = Song.objects.filter(is_approved=True).select_related('artist', 'genre').order_by('-plays')[:10]
        print(f"🔥 Found {len(most_played)} most played songs")

        # Most downloaded songs (for top charts)
        most_downloaded = Song.objects.filter(is_approved=True).select_related('artist', 'genre').order_by('-downloads')[:10]
        print(f"📥 Found {len(most_downloaded)} most downloaded songs")

        # New artists
        from artists.models import Artist
        new_artists = Artist.objects.annotate(
            total_songs=Count('songs', filter=Q(songs__is_approved=True)),
            total_plays=Sum('songs__plays')
        ).order_by('-created_at')[:8]
        print(f"👤 Found {len(new_artists)} new artists")

        # Trending artists (based on recent plays)
        seven_days_ago = timezone.now() - timedelta(days=7)
        trending_artists = Artist.objects.annotate(
            weekly_plays=Count('songs__play_history', filter=Q(songs__play_history__played_at__gte=seven_days_ago)),
            followers_count=Count('followers')
        ).order_by('-weekly_plays')[:8]
        print(f"📈 Found {len(trending_artists)} trending artists")

        # Get stats for the homepage
        total_songs = Song.objects.filter(is_approved=True).count()
        total_plays = SongPlay.objects.count()
        total_downloads = SongDownload.objects.count()
        total_artists = Artist.objects.count()
        print(f"📊 Stats - Songs: {total_songs}, Plays: {total_plays}, Downloads: {total_downloads}, Artists: {total_artists}")

        # News data - handle cases where news app might not be available
        featured_news = []
        trending_news = []
        
        try:
            from news.models import NewsArticle
            featured_news = NewsArticle.objects.filter(
                is_featured=True, 
                is_published=True
            ).order_by('-published_date')[:2]
            
            trending_news = NewsArticle.objects.filter(
                is_published=True
            ).order_by('-views', '-published_date')[:6]
            
            print(f"📰 Found {len(featured_news)} featured news and {len(trending_news)} trending news")
            
        except ImportError:
            print("ℹ️ News app not available")
        except Exception as news_error:
            print(f"⚠️ News data error: {news_error}")

        context = {
            'featured_songs': featured_songs,
            'most_played': most_played,
            'most_downloaded': most_downloaded,
            'new_artists': new_artists,
            'trending_artists': trending_artists,
            'total_songs': total_songs,
            'total_plays': total_plays,
            'total_downloads': total_downloads,
            'total_artists': total_artists,
            'featured_news': featured_news,
            'trending_news': trending_news,
            'current_date': timezone.now(),
        }
        
        print("✅ Home view context prepared successfully")
        return render(request, 'music/home.html', context)
        
    except Exception as e:
        print(f"❌ Home view error: {e}")
        import traceback
        traceback.print_exc()
        
        context = {
            'featured_songs': [],
            'most_played': [],
            'most_downloaded': [],
            'new_artists': [],
            'trending_artists': [],
            'total_songs': 0,
            'total_plays': 0,
            'total_downloads': 0,
            'total_artists': 0,
            'featured_news': [],
            'trending_news': [],
            'current_date': timezone.now(),
        }
        return render(request, 'music/home.html', context)

def discover(request):
    """Discover page with all songs"""
    songs_list = Song.objects.filter(is_approved=True).select_related('artist', 'genre').order_by('-upload_date')
    genres = Genre.objects.all()
    
    # Filtering
    genre_filter = request.GET.get('genre')
    if genre_filter:
        songs_list = songs_list.filter(genre_id=genre_filter)
    
    search_query = request.GET.get('q')
    if search_query:
        songs_list = songs_list.filter(
            Q(title__icontains=search_query) |
            Q(artist__name__icontains=search_query) |
            Q(genre__name__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(songs_list, 20)
    page_number = request.GET.get('page')
    songs = paginator.get_page(page_number)
    
    context = {
        'songs': songs,
        'genres': genres,
        'selected_genre': genre_filter,
        'search_query': search_query or '',
    }
    return render(request, 'music/discover.html', context)

def song_detail(request, song_id):
    """Individual song detail page"""
    song = get_object_or_404(
        Song.objects.select_related('artist', 'genre'), 
        id=song_id, 
        is_approved=True
    )
    
    # Check if user can access premium content
    can_access = song.can_be_accessed_by(request.user)
    
    # Get similar songs (same genre and artist)
    similar_songs = Song.objects.filter(
        genre=song.genre,
        is_approved=True
    ).exclude(id=song.id).select_related('artist', 'genre').order_by('-plays')[:6]
    
    # Get play statistics
    play_stats = SongPlay.objects.filter(song=song).aggregate(
        total_plays=Count('id'),
        avg_duration=Avg('duration_played')
    )
    
    context = {
        'song': song,
        'similar_songs': similar_songs,
        'can_access': can_access,
        'play_stats': play_stats,
    }
    return render(request, 'music/song_detail.html', context)
def search(request):
    """Smart search that handles phrases and individual words"""
    query = request.GET.get('q', '').strip()
    
    if not query:
        return redirect('discover')
    
    # Check if query contains common separators
    common_separators = [' by ', ' ft ', ' featuring ', ' feat ', ' vs ', ' and ']
    
    # Try to split by common separators first
    phrase_parts = [query]
    for separator in common_separators:
        if separator in query.lower():
            phrase_parts = query.lower().split(separator)
            break
    
    # Also split by spaces for individual words
    all_search_terms = []
    for part in phrase_parts:
        all_search_terms.extend(part.strip().split())
    
    # Remove duplicates but preserve order
    from collections import OrderedDict
    search_terms = list(OrderedDict.fromkeys(all_search_terms))
    
    print(f"🔍 Search terms: {search_terms}")
    print(f"🔍 Original query: '{query}'")
    
    # Build Q objects
    from django.db.models import Q
    
    # First try exact phrase match
    exact_phrase_q = Q(title__icontains=query) | \
                     Q(artist__name__icontains=query) | \
                     Q(lyrics__icontains=query)
    
    # Then try individual terms
    individual_terms_q = Q()
    for term in search_terms:
        if len(term) > 2:  # Only search for terms longer than 2 characters
            individual_terms_q |= Q(title__icontains=term) | \
                                 Q(artist__name__icontains=term) | \
                                 Q(genre__name__icontains=term) | \
                                 Q(lyrics__icontains=term) | \
                                 Q(featured_artists__name__icontains=term)
    
    # Combine both (exact phrase gets priority)
    final_q = exact_phrase_q | individual_terms_q
    
    # Apply filter
    songs = Song.objects.filter(
        final_q,
        is_approved=True
    ).select_related('artist', 'genre').prefetch_related('featured_artists').distinct().order_by('-plays')[:50]
    
    # Get related artists
    from artists.models import Artist
    
    artist_q = Q()
    for term in search_terms:
        if len(term) > 2:
            artist_q |= Q(name__icontains=term) | Q(bio__icontains=term)
    
    related_artists = Artist.objects.filter(artist_q).distinct()[:10]
    
    # Get related genres
    genre_q = Q()
    for term in search_terms:
        if len(term) > 2:
            genre_q |= Q(name__icontains=term) | Q(description__icontains=term)
    
    related_genres = Genre.objects.filter(genre_q).distinct()[:8]
    
    context = {
        'songs': songs,
        'related_artists': related_artists,
        'related_genres': related_genres,
        'query': query,
        'results_count': len(songs) + len(related_artists) + len(related_genres),
        'search_terms_debug': search_terms,  # For debugging
    }
    
    return render(request, 'music/search.html', context)
def genres(request):
    """All genres page"""
    genres = Genre.objects.annotate(
        song_count=Count('songs', filter=Q(songs__is_approved=True)),
        total_plays=Sum('songs__plays'),
        total_downloads=Sum('songs__downloads')
    ).filter(song_count__gt=0).order_by('name')
    
    context = {
        'genres': genres,
    }
    return render(request, 'music/genres.html', context)

def genre_songs(request, genre_id):
    """Songs by specific genre"""
    genre = get_object_or_404(Genre, id=genre_id)
    songs = Song.objects.filter(
        genre=genre, 
        is_approved=True
    ).select_related('artist', 'genre').order_by('-upload_date')
    
    # Get genre statistics
    genre_stats = songs.aggregate(
        total_songs=Count('id'),
        total_plays=Sum('plays'),
        total_downloads=Sum('downloads')
    )
    
    context = {
        'genre': genre,
        'songs': songs,
        'genre_stats': genre_stats,
    }
    return render(request, 'music/genre_songs.html', context)

# ========== PLAY SONG FUNCTION ==========
def play_song(request, song_id):
    """Play song and increment play count - ALLOW ANONYMOUS USERS"""
    try:
        song = get_object_or_404(Song, id=song_id)
        
        print(f"🎵 Play song request: {song.title} (ID: {song_id})")
        print(f"📊 Current plays before: {song.plays}")
        
        # Check access for premium content
        if not song.can_be_accessed_by(request.user):
            print("🔒 Premium content restriction")
            return JsonResponse({
                'error': 'Premium content requires subscription',
                'can_preview': song.preview_duration > 0,
                'preview_duration': song.preview_duration,
                'success': False
            }, status=403)
        
        # Use atomic update to prevent race conditions
        with transaction.atomic():
            # Increment play count atomically
            song = Song.objects.filter(id=song_id).select_for_update().first()
            if not song:
                return JsonResponse({'error': 'Song not found', 'success': False}, status=404)
            
            current_plays = song.plays
            song.plays = F('plays') + 1
            song.save()
            
            # Refresh to get updated count
            song.refresh_from_db()
            
            print(f"📈 Plays incremented atomically: {current_plays} → {song.plays}")
            
        # Record play in SongPlay model
        try:
            # For authenticated users, store user info
            if request.user.is_authenticated:
                audio_quality = 'high' if hasattr(request.user, 'userprofile') and request.user.userprofile.is_premium else 'standard'
                user = request.user
            else:
                # For anonymous users
                audio_quality = 'standard'
                user = None
            
            SongPlay.objects.create(
                song=song,
                user=user,
                ip_address=get_client_ip(request),
                duration_played=0,
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                audio_quality=audio_quality,
            )
            print("📝 SongPlay record created successfully")
        except Exception as e:
            print(f"⚠️ Error creating SongPlay record: {e}")
            # Don't fail the entire request if recording fails
        
        print(f"🎯 Final confirmed plays count: {song.plays}")
        
        return JsonResponse({
            'id': song.id,
            'title': song.title,
            'artist': song.artist.name,
            'cover': song.cover_image.url if song.cover_image else '/static/images/default-cover.jpg',
            'audio': song.audio_file.url,
            'duration': song.duration,
            'plays': song.plays,
            'is_premium': song.is_premium_only,
            'success': True,
            'message': 'Play counted successfully'
        })
        
    except Exception as e:
        print(f"❌ Error in play_song: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'error': 'Internal server error',
            'success': False
        }, status=500)

# ========== DIRECT PLAYS ENDPOINT ==========
def increment_plays_direct(request, song_id):
    """Direct endpoint to increment plays (useful for testing)"""
    if request.method == 'POST':
        try:
            song = get_object_or_404(Song, id=song_id)
            
            # Get current plays
            current_plays = song.plays
            
            # Increment using atomic transaction
            with transaction.atomic():
                song.plays = F('plays') + 1
                song.save()
                song.refresh_from_db()
            
            return JsonResponse({
                'success': True,
                'song_id': song_id,
                'title': song.title,
                'previous_plays': current_plays,
                'new_plays': song.plays,
                'incremented_by': 1
            })
        except Exception as e:
            print(f"❌ Error in increment_plays_direct: {e}")
            import traceback
            traceback.print_exc()
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid method'})

# ========== TRACK PLAY ENDPOINT ==========
def track_play(request, song_id):
    """Simple endpoint to track plays without audio streaming"""
    if request.method == 'POST':
        try:
            song = get_object_or_404(Song, id=song_id)
            
            print(f"🎵 Track play request: {song.title} (ID: {song_id})")
            print(f"📊 Current plays before: {song.plays}")
            
            # Check access for premium content
            if not song.can_be_accessed_by(request.user):
                return JsonResponse({
                    'success': False,
                    'error': 'Premium content requires subscription'
                }, status=403)
            
            # Get current plays before increment
            current_plays = song.plays
            
            # Use atomic update
            with transaction.atomic():
                # Use F() expression for atomic increment
                Song.objects.filter(id=song_id).update(plays=F('plays') + 1)
                song.refresh_from_db()
                print(f"✅ Database update successful: {current_plays} → {song.plays}")
            
            # Record play in SongPlay model (optional)
            try:
                SongPlay.objects.create(
                    song=song,
                    user=request.user if request.user.is_authenticated else None,
                    ip_address=get_client_ip(request),
                    duration_played=0,
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    audio_quality='standard',
                )
                print("📝 SongPlay record created")
            except Exception as e:
                print(f"⚠️ Error creating SongPlay record: {e}")
                # Don't fail the entire request
            
            return JsonResponse({
                'success': True,
                'song_id': song_id,
                'title': song.title,
                'previous_plays': current_plays,
                'new_plays': song.plays,
                'message': 'Play tracked successfully'
            })
            
        except Exception as e:
            print(f"❌ Error in track_play: {e}")
            import traceback
            traceback.print_exc()
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid method'})

# ========== DOWNLOAD SONG WITH BRANDING ==========
def download_song(request, song_id):
    """Download song with Sangabiz branding - FREE FOR ALL USERS"""
    song = get_object_or_404(Song, id=song_id, is_approved=True)
    
    print(f"⬇️ Download request: {song.title} (ID: {song_id})")
    print(f"📊 Current downloads before: {song.downloads}")
    
    # Check premium access
    if song.is_premium_only and not song.can_be_accessed_by(request.user):
        if not request.user.is_authenticated:
            messages.error(request, 'This is a premium song. Please log in and subscribe to download.')
        else:
            messages.error(request, 'This is a premium song. Please subscribe to download.')
        return redirect('song_detail', song_id=song_id)
    
    try:
        # Create temporary file for the branded audio
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_audio:
            temp_audio_path = temp_audio.name
        
        # Copy original audio to temp location
        print(f"📁 Copying audio from: {song.audio_file.path}")
        shutil.copy2(song.audio_file.path, temp_audio_path)
        print(f"✅ Copied audio to temp file: {temp_audio_path}")
        
        # Prepare branding
        cover_path = None
        logo_path = None
        
        # Try to find Sangabiz logo (check multiple locations)
        possible_logo_paths = [
            # First priority: logo.jpeg in various locations
            os.path.join(settings.STATIC_ROOT, 'images', 'logo.jpeg'),
            os.path.join(settings.MEDIA_ROOT, 'logos', 'logo.jpeg'),
            os.path.join(settings.BASE_DIR, 'static', 'images', 'logo.jpeg'),
            # Fallback: other image formats
            os.path.join(settings.STATIC_ROOT, 'images', 'logo.png'),
            os.path.join(settings.STATIC_ROOT, 'images', 'logo.jpg'),
            os.path.join(settings.MEDIA_ROOT, 'logos', 'logo.png'),
            os.path.join(settings.MEDIA_ROOT, 'logos', 'logo.jpg'),
            os.path.join(settings.BASE_DIR, 'static', 'images', 'logo.png'),
            os.path.join(settings.BASE_DIR, 'static', 'images', 'logo.jpg'),
        ]
        
        for possible_path in possible_logo_paths:
            if os.path.exists(possible_path):
                logo_path = possible_path
                print(f"✅ Found logo: {logo_path}")
                break
        
        if not logo_path:
            print("ℹ️ No logo found, will create text-only branding")
        
        # Create branded cover (logo replaces song cover)
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_cover:
                cover_path = temp_cover.name
            
            create_branded_cover(song, logo_path, cover_path)
            
            if os.path.exists(cover_path) and os.path.getsize(cover_path) > 0:
                print(f"✅ Created logo-only cover: {cover_path} ({os.path.getsize(cover_path)} bytes)")
            else:
                print("⚠️ Cover creation failed or empty file")
                cover_path = None
        except Exception as e:
            print(f"⚠️ Error creating branded cover: {e}")
            cover_path = None
        
        # Add metadata to audio
        metadata_success = False
        try:
            if cover_path and os.path.exists(cover_path):
                metadata_success = add_metadata_to_audio(temp_audio_path, song, cover_path, logo_path)
            else:
                print("ℹ️ No cover, trying metadata without cover")
                metadata_success = add_metadata_to_audio(temp_audio_path, song, None, logo_path)
        except Exception as e:
            print(f"⚠️ Error adding metadata: {e}")
        
        if not metadata_success:
            print("ℹ️ Metadata addition failed, but audio will still download")
        
        # Update download count
        with transaction.atomic():
            song.refresh_from_db()
            song.downloads = F('downloads') + 1
            song.save()
            song.refresh_from_db()
            print(f"📈 Downloads incremented to: {song.downloads}")
        
        # Record download
        try:
            SongDownload.objects.create(
                song=song,
                user=request.user if request.user.is_authenticated else None,
                ip_address=get_client_ip(request),
                file_size=os.path.getsize(temp_audio_path),
                audio_quality=song.audio_quality,
            )
            print("📝 SongDownload record created")
        except Exception as e:
            print(f"⚠️ Error creating SongDownload: {e}")
        
        # Prepare filename (sanitize)
        safe_title = re.sub(r'[^\w\s\-_]', '', song.title).strip()
        safe_artist = re.sub(r'[^\w\s\-_]', '', song.artist.name).strip()
        
        if not safe_title:
            safe_title = "song"
        if not safe_artist:
            safe_artist = "artist"
        
        filename = f"{safe_title} - {safe_artist} - MusicCityUg.mp3"
        
        # Serve the file
        response = FileResponse(
            open(temp_audio_path, 'rb'),
            content_type='audio/mpeg'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        # Cleanup function
        def cleanup():
            try:
                if os.path.exists(temp_audio_path):
                    os.unlink(temp_audio_path)
                if cover_path and os.path.exists(cover_path):
                    os.unlink(cover_path)
            except Exception as cleanup_error:
                print(f"Cleanup error: {cleanup_error}")
        
        response.closed = cleanup
        
        print(f"✅ Download successful for: {song.title}")
        return response
        
    except FileNotFoundError as e:
        print(f"❌ File not found error: {e}")
        messages.error(request, 'Audio file not found.')
        return redirect('song_detail', song_id=song_id)
    except Exception as e:
        print(f"❌ Download error: {str(e)}")
        import traceback
        traceback.print_exc()
        messages.error(request, 'Download failed. Please try again.')
        return redirect('song_detail', song_id=song_id)

def top_songs(request):
    """Top songs page with various rankings"""
    # Most played songs
    most_played = Song.objects.filter(is_approved=True).select_related('artist', 'genre').order_by('-plays')[:20]
    
    # Most downloaded songs
    most_downloaded = Song.objects.filter(is_approved=True).select_related('artist', 'genre').order_by('-downloads')[:20]
    
    # Trending songs (last 7 days)
    seven_days_ago = timezone.now() - timedelta(days=7)
    trending = Song.objects.filter(
        is_approved=True,
        play_history__played_at__gte=seven_days_ago
    ).annotate(
        recent_plays=Count('play_history')
    ).select_related('artist', 'genre').order_by('-recent_plays')[:20]
    
    context = {
        'most_played': most_played,
        'most_downloaded': most_downloaded,
        'trending': trending,
    }
    return render(request, 'music/top_songs.html', context)

# ========== ANONYMOUS PLAY TRACKING ==========
def track_anonymous_play(request, song_id):
    """Alternative endpoint for anonymous plays (backup)"""
    if request.method == 'POST':
        try:
            song = get_object_or_404(Song, id=song_id)
            
            # Check if user can access this song
            if not song.can_be_accessed_by(request.user):
                return JsonResponse({
                    'error': 'Premium content requires subscription'
                }, status=403)
            
            # Increment play count using atomic update
            with transaction.atomic():
                song.plays = F('plays') + 1
                song.save()
                song.refresh_from_db()
            
            # Record anonymous play
            SongPlay.objects.create(
                song=song,
                user=None,
                ip_address=get_client_ip(request),
                duration_played=0,
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                audio_quality='standard',
            )
            
            return JsonResponse({
                'success': True,
                'plays': song.plays,
                'message': 'Play counted'
            })
            
        except Exception as e:
            print(f"❌ Error tracking anonymous play: {e}")
            import traceback
            traceback.print_exc()
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid method'})

# ========== GET SONG PLAYS ENDPOINT ==========
def get_song_plays(request, song_id):
    """Get current play count for a song"""
    if request.method == 'GET':
        try:
            song = get_object_or_404(Song, id=song_id)
            return JsonResponse({
                'success': True,
                'song_id': song_id,
                'plays': song.plays,
                'title': song.title
            })
        except Exception as e:
            print(f"❌ Error getting song plays: {e}")
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid method'})

# ========== BULK UPDATE PLAYS (for debugging) ==========
def bulk_update_plays(request):
    """Debug endpoint to update all song play counts from SongPlay records"""
    if request.method == 'POST' and request.user.is_superuser:
        try:
            from django.db.models import Count
            updated_songs = []
            
            # Get all songs with their actual play counts from SongPlay
            songs = Song.objects.all()
            for song in songs:
                actual_plays = SongPlay.objects.filter(song=song).count()
                if song.plays != actual_plays:
                    song.plays = actual_plays
                    song.save()
                    updated_songs.append({
                        'id': song.id,
                        'title': song.title,
                        'old_plays': song.plays,
                        'new_plays': actual_plays
                    })
            
            return JsonResponse({
                'success': True,
                'updated_count': len(updated_songs),
                'updated_songs': updated_songs
            })
            
        except Exception as e:
            print(f"❌ Error in bulk_update_plays: {e}")
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Unauthorized'})

# ========== TRACK DOWNLOAD ANALYTICS ==========
def track_download(request):
    """Track download analytics"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            song_id = data.get('song_id')
            song_title = data.get('song_title')
            artist_name = data.get('artist_name')
            
            # Optional: Log this to analytics
            print(f"Download analytics: {song_title} by {artist_name}")
            
            return JsonResponse({'success': True})
        except:
            return JsonResponse({'success': False})
    return JsonResponse({'success': False})

# ========== TRACK PARTIAL PLAY ==========
def track_partial_play(request, song_id):
    """Track partial play when user pauses"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            current_time = data.get('current_time', 0)
            
            # Find the most recent play for this user and song
            if request.user.is_authenticated:
                play = SongPlay.objects.filter(
                    song_id=song_id,
                    user=request.user
                ).order_by('-played_at').first()
            else:
                # For anonymous users, track by IP
                play = SongPlay.objects.filter(
                    song_id=song_id,
                    ip_address=get_client_ip(request),
                    user=None
                ).order_by('-played_at').first()
            
            if play:
                play.duration_played = current_time
                play.save()
                
            return JsonResponse({'success': True})
        except:
            return JsonResponse({'success': False})
    return JsonResponse({'success': False})

# ========== UPDATE PLAY DURATION ==========
def update_play_duration(request, song_id):
    """Update play duration when playback ends"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            duration_played = data.get('duration_played', 0)
            
            # Find the most recent play for this user and song
            if request.user.is_authenticated:
                play = SongPlay.objects.filter(
                    song_id=song_id,
                    user=request.user
                ).order_by('-played_at').first()
            else:
                # For anonymous users, track by IP
                play = SongPlay.objects.filter(
                    song_id=song_id,
                    ip_address=get_client_ip(request),
                    user=None
                ).order_by('-played_at').first()
            
            if play:
                play.duration_played = duration_played
                play.save()
                
            return JsonResponse({'success': True})
            
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'})
    
    return JsonResponse({'success': False, 'error': 'Invalid method'})

# ========== LIKE SONG FUNCTION ==========
@login_required
def like_song(request, song_id):
    """Like/unlike a song"""
    if request.method == 'POST':
        try:
            song = get_object_or_404(Song, id=song_id)
            user = request.user
            
            # Check if user already liked the song
            if user in song.likes.all():
                # Unlike
                song.likes.remove(user)
                action = 'unliked'
                message = 'Removed from liked songs'
            else:
                # Like
                song.likes.add(user)
                action = 'liked'
                message = 'Added to liked songs'
            
            return JsonResponse({
                'status': 'success',
                'action': action,
                'message': message,
                'likes_count': song.likes.count()
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid method'
    })



# ========== ERROR HANDLERS ==========
def custom_404(request, exception):
    """Custom 404 error page"""
    return render(request, "music/404.html", status=404)
