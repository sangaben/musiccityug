# artists/admin.py
from django.contrib import admin
from django.db.models import Count, Sum
from django.utils.html import format_html
from .models import Artist, Follow

@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'email', 'genre', 'is_verified', 
        'created_at', 'total_songs', 'total_plays', 'followers_count'
    ]
    list_filter = ['is_verified', 'genre', 'created_at']
    search_fields = ['name', 'email', 'website', 'bio']
    readonly_fields = ['created_at', 'updated_at', 'followers_count_display']
    list_editable = ['is_verified']
    list_per_page = 25

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'email', 'genre')
        }),
        ('Profile Details', {
            'fields': ('bio', 'image', 'website')
        }),
        ('Statistics', {
            'fields': ('followers_count_display',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def total_songs(self, obj):
        return obj.songs.count() if hasattr(obj, 'songs') else 0
    total_songs.short_description = 'Total Songs'

    def total_plays(self, obj):
        if hasattr(obj, 'songs'):
            total = obj.songs.aggregate(total_plays=Sum('plays'))['total_plays']
            return total or 0
        return 0
    total_plays.short_description = 'Total Plays'

    def followers_count(self, obj):
        if hasattr(obj, '_followers_count'):
            return obj._followers_count
        return obj.followers.count()
    followers_count.short_description = 'Followers'

    def followers_count_display(self, obj):
        return obj.followers.count()
    followers_count_display.short_description = 'Number of Followers'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # Annotate followers for list view
        queryset = queryset.annotate(_followers_count=Count('followers', distinct=True))
        return queryset.select_related('genre')

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ['artist', 'follower', 'followed_at']
    list_filter = ['followed_at']
    search_fields = ['artist__name', 'follower__username']
    readonly_fields = ['followed_at']
    list_per_page = 50

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('artist', 'follower')
