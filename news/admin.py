from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.http import HttpResponse
import csv
from .models import NewsArticle, NewsComment

# Custom Admin Filters
class PublishedStatusFilter(admin.SimpleListFilter):
    title = 'publication status'
    parameter_name = 'pub_status'

    def lookups(self, request, model_admin):
        return (
            ('published', 'Published'),
            ('draft', 'Draft'),
            ('scheduled', 'Scheduled'),
            ('featured', 'Featured'),
        )

    def queryset(self, request, queryset):
        now = timezone.now()
        if self.value() == 'published':
            return queryset.filter(is_published=True, published_date__lte=now)
        elif self.value() == 'draft':
            return queryset.filter(is_published=False)
        elif self.value() == 'scheduled':
            return queryset.filter(is_published=True, published_date__gt=now)
        elif self.value() == 'featured':
            return queryset.filter(is_featured=True)

# Inline Admin for Comments
class NewsCommentInline(admin.TabularInline):
    model = NewsComment
    extra = 0
    fields = ('user', 'content_preview', 'created_date', 'is_approved')
    readonly_fields = ('content_preview', 'created_date')
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Comment Preview'

    def has_add_permission(self, request, obj=None):
        return False

# News Article Admin
@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = (
        'title_preview',
        'category_display',
        'author',
        'published_date',
        'status_display',
        'is_featured',
        'views',
        'comment_count',
    )
    
    list_filter = (
        PublishedStatusFilter,
        'category',
        'is_featured',
        'published_date',
    )
    
    search_fields = ('title', 'excerpt', 'content', 'author__username', 'tags')
    list_editable = ('is_featured',)
    readonly_fields = ('views', 'updated_date', 'comment_count_display')
    date_hierarchy = 'published_date'
    list_per_page = 25
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'title',
                'slug',
                'excerpt',
                'content',
                'featured_image',
                'tags'
            )
        }),
        ('Categorization', {
            'fields': (
                'category',
                'author',
            )
        }),
        ('Publication Settings', {
            'fields': (
                'is_published',
                'is_featured',
                'published_date',
            )
        }),
        ('Statistics & Metadata', {
            'fields': (
                'views',
                'comment_count_display',
                'updated_date',
            ),
            'classes': ('collapse',)
        }),
    )
    
    prepopulated_fields = {'slug': ('title',)}
    inlines = [NewsCommentInline]
    
    actions = [
        'publish_selected',
        'unpublish_selected',
        'feature_selected',
        'unfeature_selected',
        'export_to_csv'
    ]
    
    def title_preview(self, obj):
        return obj.title[:60] + '...' if len(obj.title) > 60 else obj.title
    title_preview.short_description = 'Title'
    
    def category_display(self, obj):
        return obj.get_category_display()
    category_display.short_description = 'Category'
    
    def status_display(self, obj):
        now = timezone.now()
        if not obj.is_published:
            return format_html('<span style="color: orange; font-weight: bold;">DRAFT</span>')
        elif obj.published_date > now:
            return format_html('<span style="color: blue; font-weight: bold;">SCHEDULED</span>')
        else:
            return format_html('<span style="color: green; font-weight: bold;">PUBLISHED</span>')
    status_display.short_description = 'Status'
    
    def comment_count(self, obj):
        return obj.comments.count()
    comment_count.short_description = 'Comments'
    
    def comment_count_display(self, obj):
        return obj.comments.count()
    comment_count_display.short_description = 'Total Comments'
    
    def publish_selected(self, request, queryset):
        updated = queryset.update(is_published=True)
        self.message_user(request, f'Successfully published {updated} article(s).')
    publish_selected.short_description = "Publish selected articles"
    
    def unpublish_selected(self, request, queryset):
        updated = queryset.update(is_published=False)
        self.message_user(request, f'Successfully unpublished {updated} article(s).')
    unpublish_selected.short_description = "Unpublish selected articles"
    
    def feature_selected(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'Successfully featured {updated} article(s).')
    feature_selected.short_description = "Feature selected articles"
    
    def unfeature_selected(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'Successfully unfeatured {updated} article(s).')
    unfeature_selected.short_description = "Unfeature selected articles"
    
    def export_to_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="news_articles.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Title', 'Category', 'Author', 'Published Date', 'Views', 'Comments', 'Is Published', 'Is Featured'
        ])
        
        for article in queryset:
            writer.writerow([
                article.title,
                article.get_category_display(),
                article.author.username,
                article.published_date.strftime('%Y-%m-%d %H:%M'),
                article.views,
                article.comments.count(),
                article.is_published,
                article.is_featured
            ])
        
        return response
    export_to_csv.short_description = "Export selected articles to CSV"
    
    def save_model(self, request, obj, form, change):
        if not obj.author_id:
            obj.author = request.user
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author').prefetch_related('comments')

# News Comment Admin
@admin.register(NewsComment)
class NewsCommentAdmin(admin.ModelAdmin):
    list_display = (
        'content_preview',
        'article_title',
        'user',
        'created_date',
        'is_approved',
    )
    
    list_filter = (
        'is_approved',
        'created_date',
        'article__category'
    )
    
    search_fields = (
        'content',
        'user__username',
        'article__title'
    )
    
    list_editable = ('is_approved',)
    readonly_fields = ('created_date',)
    list_per_page = 25
    
    actions = ['approve_comments', 'disapprove_comments']
    
    fieldsets = (
        ('Comment Content', {
            'fields': ('article', 'user', 'content')
        }),
        ('Moderation', {
            'fields': ('is_approved', 'created_date')
        }),
    )
    
    def content_preview(self, obj):
        return obj.content[:75] + '...' if len(obj.content) > 75 else obj.content
    content_preview.short_description = 'Comment'
    
    def article_title(self, obj):
        return obj.article.title[:50] + '...' if len(obj.article.title) > 50 else obj.article.title
    article_title.short_description = 'Article'
    
    def approve_comments(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'Successfully approved {updated} comment(s).')
    approve_comments.short_description = "Approve selected comments"
    
    def disapprove_comments(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'Successfully disapproved {updated} comment(s).')
    disapprove_comments.short_description = "Disapprove selected comments"