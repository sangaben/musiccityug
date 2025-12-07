# payments/admin.py
from django.contrib import admin
from .models import SubscriptionPlan, Payment

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'plan_type', 'price_monthly', 'price_yearly', 'is_active', 'created_at']
    list_filter = ['plan_type', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['is_active', 'price_monthly', 'price_yearly']
    readonly_fields = ['created_at']
    list_per_page = 20
    
    fieldsets = (
        ('Plan Information', {
            'fields': ('name', 'plan_type', 'description')
        }),
        ('Pricing', {
            'fields': ('price_monthly', 'price_yearly')
        }),
        ('Features', {
            'fields': ('features',)
        }),
        ('Stripe Integration', {
            'fields': ('stripe_price_id',),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'amount', 'status', 'created_at', 'completed_at']
    list_filter = ['status', 'created_at', 'plan']
    search_fields = ['user__username', 'stripe_payment_intent_id']
    readonly_fields = ['created_at', 'completed_at']
    list_per_page = 50
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('user', 'plan', 'amount', 'status')
        }),
        ('Stripe Information', {
            'fields': ('stripe_payment_intent_id',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'completed_at')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'plan')