from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfile

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fieldsets = (
        ('User Type', {'fields': ('user_type',)}),
        ('Profile Information', {'fields': ('bio', 'profile_picture', 'location', 'website', 'date_of_birth')}),
        ('Premium Subscription', {'fields': ('premium_plan', 'premium_since', 'premium_expires')}),
        ('Stripe Information', {'fields': ('stripe_customer_id', 'stripe_subscription_id'), 'classes': ('collapse',)}),
        ('Usage Tracking', {'fields': ('offline_downloads_used', 'max_offline_downloads'), 'classes': ('collapse',)}),
    )

class CustomUserAdmin(UserAdmin):
    inlines = [UserProfileInline]
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'get_user_type', 'get_premium_status']
    list_filter = UserAdmin.list_filter + ('userprofile__user_type', 'userprofile__premium_plan')
    
    def get_user_type(self, obj):
        return obj.userprofile.get_user_type_display()
    get_user_type.short_description = 'User Type'
    
    def get_premium_status(self, obj):
        return "Premium" if obj.userprofile.is_premium_active else "Free"
    get_premium_status.short_description = 'Premium Status'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('userprofile')

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'user_type', 'premium_plan', 'is_premium_active', 'premium_expires', 'created_at']
    list_filter = ['user_type', 'premium_plan', 'created_at']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User Information', {'fields': ('user', 'user_type')}),
        ('Profile Details', {'fields': ('bio', 'profile_picture', 'location', 'website', 'date_of_birth')}),
        ('Premium Subscription', {'fields': ('premium_plan', 'premium_since', 'premium_expires')}),
        ('Stripe Information', {'fields': ('stripe_customer_id', 'stripe_subscription_id')}),
        ('Usage Tracking', {'fields': ('offline_downloads_used', 'max_offline_downloads')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    
    def is_premium_active(self, obj):
        return obj.is_premium_active
    is_premium_active.boolean = True
    is_premium_active.short_description = 'Premium Active'
