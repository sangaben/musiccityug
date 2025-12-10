# sangabiz/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('music.urls')),
    path('', include('accounts.urls')),
    path('', include('artist.urls')),
    path('', include('library.urls')),
    path('', include('payments.urls')),
    path('', include('analytics.urls')),
]

# Add these handler definitions
handler404 = 'music.views.custom_404'  # Should accept (request, exception)
handler500 = 'music.views.custom_500'  # Should accept (request) only

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)