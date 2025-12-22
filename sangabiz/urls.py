from django.urls import path, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from .sitemaps import StaticSitemap, ArtistSitemap, SongSitemap, NewsSitemap

sitemaps = {
    'static': StaticSitemap,
    'artists': ArtistSitemap,
    'songs': SongSitemap,
    'news': NewsSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),

    # 🔴 ADD THIS LINE (only new one)
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}),

    path('', include('music.urls')),
    path('', include('accounts.urls')),
    path('', include('artists.urls')),
    path('', include('library.urls')),
    path('', include('payments.urls')),
    path('', include('analytics.urls')),
    path('', include('help.urls')),
    path('', include('news.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = "music.views.custom_404"
