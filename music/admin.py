# music/admin.py - FIXED VERSION
from django.contrib import admin
from django.utils.html import format_html
from django import forms
from django.utils import timezone
from django.urls import reverse
from .models import Genre, Song, SongPlay, SongDownload

class SongAdminForm(forms.ModelForm):
    class Meta:
        model = Song
        fields = '__all__'
    
    def clean(self):
        cleaned_data = super().clean()
        duration_minutes = cleaned_data.get('duration_minutes')
        duration_seconds = cleaned_data.get('duration_seconds')
        
        # Validate duration
        if duration_minutes is not None and duration_minutes < 0:
            self.add_error('duration_minutes', 'Minutes cannot be negative.')
        if duration_seconds is not None:
            if duration_seconds < 0:
                self.add_error('duration_seconds', 'Seconds cannot be negative.')
            if duration_seconds >= 60:
                self.add_error('duration_seconds', 'Seconds must be less than 60.')
        
        return cleaned_data

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['name', 'color_display', 'song_count']
    search_fields = ['name', 'description']
    readonly_fields = ['song_count_display']
    
    def color_display(self, obj):
        return format_html(
            '<span style="display: inline-block; width: 20px; height: 20px; background-color: {}; border-radius: 3px;"></span> {}',
            obj.color, obj.color
        )
    color_display.short_description = 'Color'
    
    def song_count(self, obj):
        return obj.songs.count()
    song_count.short_description = 'Songs'
    
    def song_count_display(self, obj):
        return obj.songs.count()
    song_count_display.short_description = 'Number of Songs'

@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    form = SongAdminForm
    change_form_template = 'admin/music/song/change_form.html'
    add_form_template = 'admin/music/song/change_form.html'
    
    list_display = [
        'title', 'artist_safe_display', 'genre', 'formatted_duration_display', 
        'plays', 'downloads', 'is_approved', 'is_featured', 'upload_date'
    ]
    list_filter = [
        'is_approved', 'is_featured', 'is_premium_only', 'genre', 
        'upload_date', 'audio_quality'
    ]
    search_fields = ['title', 'artist__name', 'genre__name', 'lyrics']
    readonly_fields = ['plays', 'downloads', 'upload_date', 'popularity_score_display', 'all_artists_safe_display']
    list_editable = ['is_approved', 'is_featured']
    list_per_page = 25
    date_hierarchy = 'upload_date'
    
    filter_horizontal = ['featured_artists']
    
    # CORRECTED fieldsets - using duration_minutes and duration_seconds
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'artist', 'featured_artists', 'genre', 'lyrics')
        }),
        ('Duration', {
            'fields': ('duration_minutes', 'duration_seconds'),
            'description': 'Enter duration in minutes (0-59) and seconds (0-59)'
        }),
        ('Media Files', {
            'fields': ('audio_file', 'cover_image')
        }),
        ('Content Settings', {
            'fields': ('is_approved', 'is_featured', 'is_premium_only', 'preview_duration', 'audio_quality')
        }),
        ('Additional Info', {
            'fields': ('bpm', 'release_year'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('plays', 'downloads', 'upload_date', 'popularity_score_display', 'all_artists_safe_display'),
            'classes': ('collapse',)
        }),
    )
    
    # Override get_fieldsets for add form
    def get_fieldsets(self, request, obj=None):
        if not obj:  # Add form
            return (
                ('Song Details', {
                    'fields': ('title', 'artist', 'featured_artists', 'genre'),
                    'classes': ('wide', 'extrapretty'),
                }),
                ('Audio Upload', {
                    'fields': ('audio_file', 'cover_image'),
                    'description': 'Upload high-quality audio files. Supported formats: MP3, WAV, FLAC'
                }),
                ('Duration', {
                    'fields': ('duration_minutes', 'duration_seconds'),
                }),
                ('Content Settings', {
                    'fields': ('is_approved', 'is_featured', 'is_premium_only', 'audio_quality'),
                }),
                ('Additional Information', {
                    'fields': ('lyrics', 'bpm', 'release_year', 'preview_duration'),
                    'classes': ('collapse',),
                }),
            )
        return super().get_fieldsets(request, obj)
    
    def artist_safe_display(self, obj):
        """Safe display without recursion."""
        try:
            return obj.artist.name if obj.artist else "Unknown"
        except Exception:
            return "Unknown"
    artist_safe_display.short_description = 'Artist'
    
    def formatted_duration_display(self, obj):
        try:
            minutes = obj.duration_minutes or 0
            seconds = obj.duration_seconds or 0
            return f"{minutes:02d}:{seconds:02d}"
        except Exception:
            return "00:00"
    formatted_duration_display.short_description = 'Duration'
    
    def all_artists_safe_display(self, obj):
        """Safe display of all artists without recursion."""
        try:
            artists = []
            if obj.artist:
                artists.append(f"Primary: {obj.artist.name}")
            
            featured = obj.featured_artists.all()
            if featured:
                featured_names = [artist.name for artist in featured]
                artists.append(f"Featured: {', '.join(featured_names)}")
            
            return format_html('<br>'.join(artists)) if artists else "-"
        except Exception:
            return "Error loading artists"
    all_artists_safe_display.short_description = 'All Artists'
    
    def popularity_score_display(self, obj):
        return obj.popularity_score
    popularity_score_display.short_description = 'Popularity Score'
    
    def save_model(self, request, obj, form, change):
        # Auto-populate upload date for new songs
        if not obj.pk:
            obj.upload_date = timezone.now()
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'artist', 'genre'
        ).prefetch_related(
            'featured_artists'
        )
    
    class Media:
        css = {
            'all': ('admin/css/song_admin.css',)
        }
        js = ('admin/js/song_admin.js',)

@admin.register(SongPlay)
class SongPlayAdmin(admin.ModelAdmin):
    list_display = ['song', 'user', 'played_at', 'duration_played', 'audio_quality', 'ip_address']
    list_filter = ['played_at', 'audio_quality']
    search_fields = ['song__title', 'user__username', 'ip_address']
    readonly_fields = ['played_at']
    list_per_page = 50
    date_hierarchy = 'played_at'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('song', 'user')

@admin.register(SongDownload)
class SongDownloadAdmin(admin.ModelAdmin):
    list_display = ['song', 'user', 'downloaded_at', 'is_offline_download', 'audio_quality']
    list_filter = ['downloaded_at', 'is_offline_download', 'audio_quality']
    search_fields = ['song__title', 'user__username', 'ip_address']
    readonly_fields = ['downloaded_at']
    list_per_page = 50
    date_hierarchy = 'downloaded_at'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('song', 'user')
