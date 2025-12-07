from django.contrib import admin
from .models import Playlist, Like

@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'song_count', 'is_public', 'created_at']
    list_filter = ['is_public', 'created_at']
    search_fields = ['name', 'user__username', 'description']
    filter_horizontal = ['songs']
    readonly_fields = ['created_at']
    list_per_page = 25
    
    fieldsets = (
        ('Basic Information', {'fields': ('name', 'user', 'description')}),
        ('Visibility', {'fields': ('is_public',)}),
        ('Media', {'fields': ('cover_image',)}),
        ('Songs', {'fields': ('songs',)}),
        ('Timestamps', {'fields': ('created_at',)}),
    )
    
    def song_count(self, obj):
        return obj.songs.count()
    song_count.short_description = 'Songs'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user').prefetch_related('songs')

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'song', 'liked_at']
    list_filter = ['liked_at']
    search_fields = ['user__username', 'song__title']
    readonly_fields = ['liked_at']
    list_per_page = 50
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'song')
