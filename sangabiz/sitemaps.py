from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from artists.models import Artist
from music.models import Song
from news.models import News


class StaticSitemap(Sitemap):
    priority = 1.0
    changefreq = "daily"

    def items(self):
        return ['home']

    def location(self, item):
        return reverse(item)


class ArtistSitemap(Sitemap):
    priority = 0.8
    changefreq = "weekly"

    def items(self):
        return Artist.objects.filter(is_verified=True)


class SongSitemap(Sitemap):
    priority = 0.7
    changefreq = "weekly"

    def items(self):
        return Song.objects.filter(is_approved=True)


class NewsSitemap(Sitemap):
    priority = 0.6
    changefreq = "weekly"

    def items(self):
        return News.objects.filter(is_published=True)
