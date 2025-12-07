# music/admin.py - FIXED VERSION
from django.contrib import admin
from django.utils.html import format_html
from .models import Genre, Song, SongPlay, SongDownload

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
    list_display = [
        'title', 'artist', 'genre', 'formatted_duration_display', 
        'plays', 'downloads', 'is_approved', 'is_featured', 'upload_date'
    ]
    list_filter = [
        'is_approved', 'is_featured', 'is_premium_only', 'genre', 
        'upload_date', 'audio_quality'
    ]
    search_fields = ['title', 'artist__name', 'genre__name', 'lyrics']
    readonly_fields = ['plays', 'downloads', 'upload_date', 'popularity_score_display']
    list_editable = ['is_approved', 'is_featured']
    list_per_page = 25
    date_hierarchy = 'upload_date'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'artist', 'genre', 'duration', 'lyrics')
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
            'fields': ('plays', 'downloads', 'upload_date', 'popularity_score_display'),
            'classes': ('collapse',)
        }),
    )
    
    def formatted_duration_display(self, obj):
        return obj.formatted_duration
    formatted_duration_display.short_description = 'Duration'
    
    def popularity_score_display(self, obj):
        return obj.popularity_score
    popularity_score_display.short_description = 'Popularity Score'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('artist', 'genre')

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