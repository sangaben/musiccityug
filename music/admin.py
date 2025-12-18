# music/admin.py - UPDATED VERSION
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
        'title', 'artist_display', 'display_artist_display', 'genre', 
        'formatted_duration_display', 'plays', 'downloads', 
        'is_approved', 'is_featured', 'upload_date'
    ]
    list_filter = [
        'is_approved', 'is_featured', 'is_premium_only', 'genre', 
        'upload_date', 'audio_quality'
    ]
    search_fields = [
        'title', 'artist__name', 'display_artist_name', 
        'genre__name', 'lyrics'
    ]
    readonly_fields = [
        'plays', 'downloads', 'upload_date', 
        'popularity_score_display', 'all_artists_safe_display',
        'actual_vs_display_comparison'
    ]
    list_editable = ['is_approved', 'is_featured']
    list_per_page = 25
    date_hierarchy = 'upload_date'
    
    filter_horizontal = ['featured_artists']
    
    # UPDATED fieldsets to include display_artist_name
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'artist', 'display_artist_name', 'featured_artists', 'genre', 'lyrics'),
            'description': 'Artist: Linked artist object. Display Artist: Optional name to show to users.'
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
            'fields': (
                'plays', 'downloads', 'upload_date', 
                'popularity_score_display', 'all_artists_safe_display',
                'actual_vs_display_comparison'
            ),
            'classes': ('collapse',)
        }),
    )
    
    # Override get_fieldsets for add form
    def get_fieldsets(self, request, obj=None):
        if not obj:  # Add form
            return (
                ('Song Details', {
                    'fields': ('title', 'artist', 'display_artist_name', 'featured_artists', 'genre'),
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
    
    def artist_display(self, obj):
        """Display the linked artist."""
        try:
            return obj.artist.name if obj.artist else "Unknown"
        except Exception:
            return "Unknown"
    artist_display.short_description = 'Linked Artist'
    artist_display.admin_order_field = 'artist__name'
    
    def display_artist_display(self, obj):
        """Display the display artist name with styling."""
        try:
            display_name = obj.get_display_artist_name()
            if obj.display_artist_name and obj.display_artist_name != str(obj.artist):
                # Display name is different from linked artist
                return format_html(
                    '<span style="color: #007bff; font-weight: bold;">{}</span>',
                    display_name
                )
            return display_name
        except Exception:
            return "Unknown"
    display_artist_display.short_description = 'Display Name'
    display_artist_display.admin_order_field = 'display_artist_name'
    
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
            
            # Primary artist
            if obj.artist:
                display_name = obj.get_display_artist_name()
                if obj.display_artist_name and obj.display_artist_name != str(obj.artist):
                    artists.append(f"Primary: {str(obj.artist)} → <strong>{display_name}</strong>")
                else:
                    artists.append(f"Primary: {display_name}")
            
            # Featured artists
            featured = obj.featured_artists.all()
            if featured:
                featured_names = [artist.name for artist in featured]
                artists.append(f"Featured: {', '.join(featured_names)}")
            
            return format_html('<br>'.join(artists)) if artists else "-"
        except Exception:
            return "Error loading artists"
    all_artists_safe_display.short_description = 'All Artists (with display names)'
    
    def actual_vs_display_comparison(self, obj):
        """Show comparison between actual artist and display name."""
        try:
            actual_name = str(obj.artist) if obj.artist else "No artist linked"
            display_name = obj.get_display_artist_name()
            
            if obj.display_artist_name and obj.display_artist_name != actual_name:
                return format_html(
                    '<div style="padding: 10px; background-color: #f8f9fa; border-radius: 5px;">'
                    '<strong>Actual:</strong> {}<br>'
                    '<strong>Display:</strong> <span style="color: #007bff;">{}</span><br>'
                    '<em style="color: #6c757d;">Display name will be shown to users</em>'
                    '</div>',
                    actual_name, display_name
                )
            else:
                return format_html(
                    '<div style="padding: 10px; background-color: #f8f9fa; border-radius: 5px;">'
                    '<strong>Actual & Display:</strong> {}<br>'
                    '<em style="color: #6c757d;">Both names are the same</em>'
                    '</div>',
                    actual_name
                )
        except Exception:
            return "Error in comparison"
    actual_vs_display_comparison.short_description = 'Artist Name Comparison'
    
    def popularity_score_display(self, obj):
        return obj.popularity_score
    popularity_score_display.short_description = 'Popularity Score'
    
    def save_model(self, request, obj, form, change):
        # Auto-populate upload date for new songs
        if not obj.pk:
            obj.upload_date = timezone.now()
        
        # If display_artist_name is empty, set it to None
        if obj.display_artist_name == '':
            obj.display_artist_name = None
            
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'artist', 'genre'
        ).prefetch_related(
            'featured_artists'
        )
    
    # Custom actions for display artist name
    actions = ['copy_artist_to_display', 'clear_display_names']
    
    def copy_artist_to_display(self, request, queryset):
        """Copy linked artist name to display artist name."""
        updated_count = 0
        for song in queryset:
            if song.artist and not song.display_artist_name:
                song.display_artist_name = str(song.artist)
                song.save()
                updated_count += 1
        
        self.message_user(
            request, 
            f'Successfully copied artist names to display names for {updated_count} songs.'
        )
    copy_artist_to_display.short_description = "Copy linked artist name to display name"
    
    def clear_display_names(self, request, queryset):
        """Clear display artist names (set to None)."""
        updated_count = queryset.update(display_artist_name=None)
        self.message_user(
            request, 
            f'Successfully cleared display names for {updated_count} songs.'
        )
    clear_display_names.short_description = "Clear display artist names"
    
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
