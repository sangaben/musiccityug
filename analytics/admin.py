# analytics/admin.py
from django.contrib import admin

# Remove the SongPlay registration since it's already in music/admin.py
# @admin.register(SongPlay)
# class SongPlayAnalyticsAdmin(admin.ModelAdmin):
#     # Remove this duplicate registration
#     pass

# Only register analytics-specific models here