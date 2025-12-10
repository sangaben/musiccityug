from django.urls import path, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('music.urls')),
    path('', include('accounts.urls')),
    path('', include('artists.urls')),
    path('', include('library.urls')),
    path('', include('payments.urls')),
    path('', include('analytics.urls')),
    path('', include('help.urls')),  # Add help URLs
    path('', include('news.urls')),  # Add news URLs    
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = "music.views.custom_404"  # Change 'music' to the app where you put the view
