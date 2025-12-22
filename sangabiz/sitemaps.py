from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from artists.models import Artist
from music.models import Song
from news.models import NewsArticle


class StaticSitemap(Sitemap):
    priority = 1.0
    changefreq = "daily"

    def items(self):
        return []

    def location(self, item):
        return "/"


class ArtistSitemap(Sitemap):
    priority = 0.8
    changefreq = "weekly"

    def items(self):
        return Artist.objects.all()


class SongSitemap(Sitemap):
    priority = 0.7
    changefreq = "weekly"

    def items(self):
        return Song.objects.all()


class NewsSitemap(Sitemap):
    priority = 0.6
    changefreq = "weekly"

    def items(self):
        return NewsArticle.objects.filter(is_published=True)
