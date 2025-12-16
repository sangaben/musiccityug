# artists/admin.py
from django.contrib import admin
from django.contrib.auth.models import User  # Add this import
from django.db.models import Sum, Count
from django.utils.html import format_html
from .models import Artist, Follow

@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ['name', 'user_linked', 'email', 'genre', 'is_verified', 'created_at', 'total_songs', 'total_plays', 'followers_count']
    list_filter = ['is_verified', 'genre', 'created_at']
    search_fields = ['name', 'email', 'website', 'bio', 'user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at', 'followers_count_display', 'user_link_display']
    list_editable = ['is_verified']
    list_per_page = 25
    
    fieldsets = (
        ('Account Information', {
            'fields': ('user', 'user_link_display', 'is_verified')
        }),
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
        # Assuming you have a Song model with foreign key to Artist
        return obj.songs.count() if hasattr(obj, 'songs') else 0
    total_songs.short_description = 'Total Songs'
    
    def total_plays(self, obj):
        if hasattr(obj, 'songs'):
            total = obj.songs.aggregate(total_plays=Sum('plays'))['total_plays']
            return total or 0
        return 0
    total_plays.short_description = 'Total Plays'
    
    def followers_count(self, obj):
        # Use annotated value if available
        if hasattr(obj, '_followers_count'):
            return obj._followers_count
        return obj.followers.count()
    followers_count.short_description = 'Followers'
    
    def followers_count_display(self, obj):
        return obj.followers.count()
    followers_count_display.short_description = 'Number of Followers'
    
    def user_linked(self, obj):
        """Display user status in list view"""
        if obj.user:
            return format_html(
                '<span style="color: green;">✓ {}</span>',
                obj.user.username
            )
        return format_html('<span style="color: gray;">No account</span>')
    user_linked.short_description = 'User Account'
    
    def user_link_display(self, obj):
        """Display user link in detail view"""
        if obj.user:
            return format_html(
                '<a href="/admin/auth/user/{}/change/">{}</a> (ID: {})',
                obj.user.id,
                obj.user.username,
                obj.user.id
            )
        return "No user account linked"
    user_link_display.short_description = 'Linked User Account'
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # Use annotate to optimize followers count in list view
        queryset = queryset.annotate(
            _followers_count=Count('followers', distinct=True)
        )
        return queryset.select_related('genre', 'user')
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Filter user field to show only users not already linked to an artist"""
        if db_field.name == "user":
            # Exclude users already linked to other artists
            kwargs["queryset"] = User.objects.filter(artist_profile__isnull=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def save_model(self, request, obj, form, change):
        # If a user is linked, ensure the email matches if not set
        if obj.user and not obj.email:
            obj.email = obj.user.email
        super().save_model(request, obj, form, change)

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ['artist', 'follower', 'followed_at']
    list_filter = ['followed_at']
    search_fields = ['artist__name', 'follower__username']
    readonly_fields = ['followed_at']
    list_per_page = 50
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('artist', 'follower')
