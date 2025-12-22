from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse


class NewsArticle(models.Model):
    CATEGORY_CHOICES = [
        ('music_news', 'Music News'),
        ('artist_spotlight', 'Artist Spotlight'),
        ('concerts', 'Concerts & Events'),
        ('releases', 'New Releases'),
        ('interviews', 'Interviews'),
        ('charts', 'Charts & Trends'),
        ('industry', 'Industry News'),
        ('culture', 'Music Culture'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    excerpt = models.TextField(max_length=300)
    content = models.TextField()
    featured_image = models.ImageField(upload_to='news/images/')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    published_date = models.DateTimeField(default=timezone.now)
    updated_date = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    views = models.PositiveIntegerField(default=0)
    tags = models.CharField(max_length=200, blank=True)
    
    class Meta:
        ordering = ['-published_date']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('news_detail', kwargs={'news_id': self.id})

class NewsComment(models.Model):
    article = models.ForeignKey(NewsArticle, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_date']
    
    def __str__(self):
        return f'Comment by {self.user.username} on {self.article.title}'
