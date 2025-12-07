# artists/admin.py
from django.contrib import admin
from django.db.models import Sum
from .models import Artist, Follow

@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'genre', 'is_verified', 'created_at', 'total_songs', 'total_plays']
    list_filter = ['is_verified', 'genre', 'created_at']
    search_fields = ['name', 'user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['is_verified']
    list_per_page = 25
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'name', 'genre', 'is_verified')
        }),
        ('Profile Details', {
            'fields': ('bio', 'image', 'website')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def total_songs(self, obj):
        return obj.songs.count()
    total_songs.short_description = 'Total Songs'
    
    def total_plays(self, obj):
        # Calculate total plays by summing plays from all songs
        total = obj.songs.aggregate(total_plays=Sum('plays'))['total_plays']
        return total or 0
    total_plays.short_description = 'Total Plays'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'genre')

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ['artist', 'follower', 'followed_at']
    list_filter = ['followed_at']
    search_fields = ['artist__name', 'follower__username']
    readonly_fields = ['followed_at']
    list_per_page = 50
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('artist', 'follower')