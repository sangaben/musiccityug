# music/admin.py - UPDATED VERSION
from django.contrib import admin
from django.utils.html import format_html
from django import forms
from django.utils import timezone
from .models import Genre, Song, SongPlay, SongDownload

class SongAdminForm(forms.ModelForm):
    class Meta:
        model = Song
        fields = '__all__'
        widgets = {
            'duration_minutes': forms.NumberInput(attrs={'min': 0, 'max': 59}),
            'duration_seconds': forms.NumberInput(attrs={'min': 0, 'max': 59}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        duration_minutes = cleaned_data.get('duration_minutes')
        duration_seconds = cleaned_data.get('duration_seconds')
        artist_name_manual = cleaned_data.get('artist_name_manual')
        artist = cleaned_data.get('artist')
        
        # Validate duration
        if duration_minutes is not None and duration_minutes < 0:
            self.add_error('duration_minutes', 'Minutes cannot be negative.')
        
        if duration_seconds is not None:
            if duration_seconds < 0:
                self.add_error('duration_seconds', 'Seconds cannot be negative.')
            if duration_seconds >= 60:
                self.add_error('duration_seconds', 'Seconds must be between 0 and 59.')
        
        # Validate artist selection
        if not artist_name_manual and not artist:
            raise forms.ValidationError(
                "You must either select an artist from the list OR enter a manual artist name."
            )
        
        # Auto-calculate total duration if audio file exists
        audio_file = cleaned_data.get('audio_file')
        if audio_file and (duration_minutes == 0 and duration_seconds == 0):
            try:
                from mutagen import File
                import tempfile
                import os
                
                # Save the file temporarily to get duration
                with tempfile.NamedTemporaryFile(delete=False) as tmp:
                    for chunk in audio_file.chunks():
                        tmp.write(chunk)
                    tmp_path = tmp.name
                
                audio = File(tmp_path)
                if audio and audio.info.length:
                    total_seconds = int(audio.info.length)
                    cleaned_data['duration_minutes'] = total_seconds // 60
                    cleaned_data['duration_seconds'] = total_seconds % 60
                
                os.unlink(tmp_path)
            except:
                pass
        
        return cleaned_data

@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    form = SongAdminForm
    change_form_template = 'admin/music/song/change_form.html'
    add_form_template = 'admin/music/song/change_form.html'
    
    # Display in list view
    list_display = [
        'title', 
        'artist_display',  # Use custom method
        'genre', 
        'formatted_duration_column',
        'plays', 
        'downloads', 
        'is_approved', 
        'is_featured', 
        'upload_date'
    ]
    
    list_filter = [
        'is_approved', 'is_featured', 'is_premium_only', 'genre', 
        'upload_date', 'audio_quality'
    ]
    
    # Search both manual and foreign key artists
    search_fields = [
        'title', 
        'artist_name_manual',  # Search manual artist names
        'artist__name',        # Search foreign key artist names
        'genre__name', 
        'lyrics'
    ]
    
    readonly_fields = [
        'plays', 'downloads', 'upload_date', 'popularity_score_display',
        'artist_info_display', 'total_duration_display'
    ]
    list_editable = ['is_approved', 'is_featured']
    list_per_page = 25
    date_hierarchy = 'upload_date'
    
    filter_horizontal = ['featured_artists']
    
    # UPDATED: Fieldsets with manual artist field
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'title', 
                ('artist_name_manual', 'artist'),  # Both manual and dropdown
                'featured_artists', 
                'genre', 
                'lyrics'
            ),
            'description': 'You can either enter an artist name manually OR select from the list. Manual entry takes precedence.'
        }),
        ('Duration', {
            'fields': ('duration_minutes', 'duration_seconds', 'total_duration_display'),
            'description': 'Enter duration in minutes and seconds. Seconds must be 0-59.'
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
            'fields': ('plays', 'downloads', 'upload_date', 'popularity_score_display', 'artist_info_display'),
            'classes': ('collapse',)
        }),
    )
    
    # Custom method to display artist in list view
    def artist_display(self, obj):
        """Display artist (manual or from foreign key)"""
        artist_name = obj.get_artist_display()
        
        # Add indicator for manual vs selected artist
        if obj.artist_name_manual:
            return format_html(
                '{} <span class="badge badge-info" style="font-size: 0.7rem;">Manual</span>',
                artist_name
            )
        elif obj.artist:
            return format_html(
                '{} <span class="badge badge-success" style="font-size: 0.7rem;">Selected</span>',
                artist_name
            )
        return artist_name
    artist_display.short_description = 'Artist'
    artist_display.admin_order_field = 'artist__name'  # Can order by foreign key
    
    def formatted_duration_column(self, obj):
        minutes = obj.duration_minutes if obj.duration_minutes is not None else 0
        seconds = obj.duration_seconds if obj.duration_seconds is not None else 0
        return f"{minutes:02d}:{seconds:02d}"
    formatted_duration_column.short_description = 'Duration'
    
    # Display total duration in seconds in admin form
    def total_duration_display(self, obj):
        total = obj.duration
        return f"Total: {total} seconds ({obj.formatted_duration})"
    total_duration_display.short_description = 'Total Duration'
    
    # Display artist info (manual vs selected)
    def artist_info_display(self, obj):
        info = []
        
        if obj.artist_name_manual:
            info.append(f"<strong>Manual Artist:</strong> {obj.artist_name_manual}")
        
        if obj.artist:
            info.append(f"<strong>Selected Artist:</strong> {obj.artist.name}")
        
        if obj.featured_artists.exists():
            featured_names = [str(artist) for artist in obj.featured_artists.all()]
            info.append(f"<strong>Featured Artists:</strong> {', '.join(featured_names)}")
        
        return format_html('<br>'.join(info)) if info else "No artist information"
    artist_info_display.short_description = 'Artist Information'
    
    def popularity_score_display(self, obj):
        return obj.popularity_score
    popularity_score_display.short_description = 'Popularity Score'
    
    def save_model(self, request, obj, form, change):
        # Auto-populate upload date for new songs
        if not obj.pk:
            obj.upload_date = timezone.now()
        
        # Auto-calculate popularity score if needed
        if not obj.popularity_score:
            obj.popularity_score = (obj.plays * 0.6) + (obj.downloads * 0.4)
        
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

# Keep your existing GenreAdmin, SongPlayAdmin, SongDownloadAdmin
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
