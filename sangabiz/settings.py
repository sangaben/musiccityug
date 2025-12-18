"""
Django settings for sangabiz project.
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# --------------------------------------------------
# Load environment variables
# --------------------------------------------------
load_dotenv()

# --------------------------------------------------
# Base Directory
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# --------------------------------------------------
# Security
# --------------------------------------------------
SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "django-insecure-p-8cakys+ff2=@ug-r__yilt%sli8bn4%3+hh30+c9$j$=^z*%"
)

DEBUG =True

ALLOWED_HOSTS = [
    "musiccityug.com",
    "www.musiccityug.com",
    "sangabiz.com",
    "www.sangabiz.com",
    "31.220.78.100",
    "127.0.0.1",
    "localhost",
]

# --------------------------------------------------
# Application Definition
# --------------------------------------------------
INSTALLED_APPS = [
    "jazzmin",
    "django.contrib.humanize",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "crispy_forms",
    "crispy_bootstrap5",

    # Custom apps
    "accounts",
    "music",
    "artists",
    "analytics",
    "payments",
    "library",
    "help",
    "news",
]

# --------------------------------------------------
# Middleware
# --------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# --------------------------------------------------
# URLs & WSGI
# --------------------------------------------------
ROOT_URLCONF = "sangabiz.urls"
WSGI_APPLICATION = "sangabiz.wsgi.application"

# --------------------------------------------------
# Templates
# --------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.media",
                "music.context_processors.genres",
            ],
        },
    },
]

# --------------------------------------------------
# Database (PostgreSQL)
# --------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME", "musiccityug"),
        "USER": os.getenv("DB_USER", "musicuser"),
        "PASSWORD": os.getenv("DB_PASSWORD", "securepassword"),
        "HOST": os.getenv("DB_HOST", "localhost"),
        "PORT": os.getenv("DB_PORT", "5432"),
        "CONN_MAX_AGE": 600,
    }
}


# --------------------------------------------------
# Password Validation
# --------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 8}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# --------------------------------------------------
# Internationalization
# --------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# --------------------------------------------------
# Static & Media Files
# --------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
os.makedirs(MEDIA_ROOT, exist_ok=True)


# Upload limits
DATA_UPLOAD_MAX_MEMORY_SIZE = 524288000  # 500MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 524288000  # 500MB


# --------------------------------------------------
# Authentication Redirects
# --------------------------------------------------
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "home"

# --------------------------------------------------
# Crispy Forms
# --------------------------------------------------
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# --------------------------------------------------
# Email Configuration
# --------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True") == "True"
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "webmaster@musiccityug.com")

# --------------------------------------------------
# Sessions
# --------------------------------------------------
SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_AGE = 1209600
SESSION_SAVE_EVERY_REQUEST = True

# --------------------------------------------------
# Production Security
# --------------------------------------------------
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = "DENY"
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# --------------------------------------------------
# Logging
# --------------------------------------------------
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "level": "ERROR",
            "class": "logging.FileHandler",
            "filename": LOGS_DIR / "django_errors.log",
        },
        "console": {"class": "logging.StreamHandler"},
    },
    "loggers": {
        "django": {"handlers": ["file", "console"], "level": "ERROR"},
    },
}

# --------------------------------------------------
# Jazzmin Configuration (Spotify-Inspired MusicCityUG Admin)
# --------------------------------------------------
SITE_URL = "https://musiccityug.com"

JAZZMIN_SETTINGS = {
    # ========== BRANDING & THEME ==========
    "site_title": "🎵 MusicCityUG Admin",
    "site_header": "🎵 MusicCityUG",
    "site_brand": "🎵 MusicCityUG",
    "site_logo": "admin/img/logo.png",
    "login_logo": "admin/img/logo.png",
    "login_logo_dark": "admin/img/logo_dark.png",
    "site_logo_classes": "img-circle",
    "site_icon": "admin/img/favicon.ico",
    "welcome_sign": "🎶 Welcome to MusicCityUG Administration",
    "copyright": "© 2025 MusicCityUG | Uganda's Sound, Your Playlist",
    "search_model": ["auth.User", "music.Song", "artists.Artist", "news.News", "payments.Transaction"],
    
    # ========== THEME & UI ==========
    "theme": "darkly",  # Matches Spotify dark theme
    "dark_mode_theme": "darkly",
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    "order_with_respect_to": [
        "music", "artists", "accounts", "payments", 
        "analytics", "library", "news", "help", "auth"
    ],
    
    # ========== CUSTOM LINKS ==========
    "topmenu_links": [
        {"name": "📊 Dashboard", "url": "admin:index", "permissions": ["auth.view_user"], "icon": "fas fa-tachometer-alt"},
        {"name": "🌍 Visit Website", "url": SITE_URL, "new_window": True, "icon": "fas fa-globe"},
        {"name": "📈 Analytics", "url": "/admin/analytics/", "permissions": ["analytics.view_analytic"], "icon": "fas fa-chart-line"},
        {"name": "💳 Payments", "url": "/admin/payments/", "permissions": ["payments.view_transaction"], "icon": "fas fa-credit-card"},
        {"app": "music", "icon": "fas fa-music"},
        {"app": "artists", "icon": "fas fa-microphone"},
        {"model": "auth.user", "icon": "fas fa-users"},
    ],
    
    "usermenu_links": [
        {"name": "🎵 MusicCityUG", "url": SITE_URL, "new_window": True, "icon": "fas fa-globe"},
        {"name": "📞 Support", "url": "/admin/help/supportticket/", "icon": "fas fa-question-circle"},
        {"name": "⚙️ Settings", "url": "/admin/auth/user/", "icon": "fas fa-cog"},
        {"model": "auth.user", "icon": "fas fa-user"},
    ],
    
    # ========== ICONS (Music-Themed) ==========
    "icons": {
        # Auth
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        
        # Music App
        "music": "fas fa-music",
        "music.Song": "fas fa-file-audio",
        "music.Album": "fas fa-compact-disc",
        "music.Genre": "fas fa-tag",
        "music.Playlist": "fas fa-list-music",
        "music.SongPlay": "fas fa-play-circle",
        "music.SongDownload": "fas fa-download",
        
        # Artists App
        "artists": "fas fa-microphone-alt",
        "artists.Artist": "fas fa-user-tie",
        "artists.Band": "fas fa-users",
        
        # Accounts
        "accounts": "fas fa-user-circle",
        "accounts.UserProfile": "fas fa-id-card",
        
        # Payments
        "payments": "fas fa-credit-card",
        "payments.Transaction": "fas fa-exchange-alt",
        "payments.Subscription": "fas fa-calendar-check",
        
        # Analytics
        "analytics": "fas fa-chart-line",
        "analytics.PlayAnalytic": "fas fa-chart-bar",
        "analytics.DownloadAnalytic": "fas fa-chart-pie",
        
        # Library
        "library": "fas fa-book",
        "library.Collection": "fas fa-folder",
        
        # Help
        "help": "fas fa-question-circle",
        "help.FAQ": "fas fa-comment-dots",
        "help.SupportTicket": "fas fa-ticket-alt",
        
        # News
        "news": "fas fa-newspaper",
        "news.Article": "fas fa-file-alt",
        "news.Category": "fas fa-folder",
    },
    
    # ========== CUSTOM ACTIONS ==========
    "custom_links": {
        "music": [
            {
                "name": "📤 Bulk Upload",
                "url": "/admin/music/song/bulk-upload/",
                "icon": "fas fa-upload",
                "permissions": ["music.add_song"]
            },
            {
                "name": "📊 Song Analytics",
                "url": "/admin/music/song/analytics/",
                "icon": "fas fa-chart-line",
                "permissions": ["analytics.view_playanalytic"]
            },
            {
                "name": "🎼 Quick Add Song",
                "url": "/admin/music/song/add/",
                "icon": "fas fa-plus-circle",
                "permissions": ["music.add_song"]
            }
        ],
        "artists": [
            {
                "name": "🌟 Featured Artists",
                "url": "/admin/artists/artist/?featured=true",
                "icon": "fas fa-star",
                "permissions": ["artists.view_artist"]
            },
            {
                "name": "👥 Add New Artist",
                "url": "/admin/artists/artist/add/",
                "icon": "fas fa-user-plus",
                "permissions": ["artists.add_artist"]
            }
        ],
    },
    
    # ========== UI SETTINGS ==========
    "show_ui_builder": True,
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {
        "auth.user": "collapsible",
        "auth.group": "vertical_tabs",
        "music.song": "horizontal_tabs",
        "artists.artist": "collapsible",
    },
    "related_modal_active": True,
    "custom_css": "admin/css/custom_admin.css",
    "custom_js": "admin/js/custom_admin.js",
    
    # ========== DASHBOARD WIDGETS ==========
    "show_dashboard_stats": True,
    "dashboard_widgets": [
        {
            "type": "app_list",
            "title": "🚀 Quick Access",
            "icon": "fas fa-rocket",
            "order": "DESC",
            "models": ["music.song", "artists.artist", "payments.transaction", "analytics.playanalytic"]
        },
        {
            "type": "list",
            "title": "🎵 Recent Songs",
            "icon": "fas fa-music",
            "url_name": "admin:music_song_changelist",
            "limit": 5,
            "order_by": "-upload_date",
            "columns": ["title", "artist", "upload_date"]
        },
        {
            "type": "list",
            "title": "🌟 Top Artists",
            "icon": "fas fa-microphone",
            "url_name": "admin:artists_artist_changelist",
            "limit": 5,
            "order_by": "-total_plays",
            "columns": ["name", "total_plays", "song_count"]
        },
        {
            "type": "chart",
            "title": "📈 Daily Plays",
            "icon": "fas fa-chart-line",
            "url_name": "admin:daily_plays_chart",
            "interval": "day",
            "limit": 7
        },
    ],
    
    # ========== LANGUAGE ==========
    "language_chooser": False,
}

# Enhanced UI Tweaks for Spotify Theme
JAZZMIN_UI_TWEAKS = {
    "theme": "darkly",
    "dark_mode_theme": "darkly",
    
    # Navbar
    "navbar": "navbar-dark navbar-primary",
    "navbar_fixed": True,
    "navbar_small_text": False,
    "navbar_brand_text": "🎵",
    
    # Sidebar
    "sidebar": "sidebar-dark-primary",
    "sidebar_fixed": True,
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    
    # Footer
    "footer_fixed": False,
    
    # Cards
    "card": "card-outline card-primary",
    "card_border": True,
    "card_header_border": True,
    
    # Buttons
    "button_classes": {
        "primary": "btn-outline-primary",
        "secondary": "btn-outline-secondary",
        "info": "btn-outline-info",
        "warning": "btn-outline-warning",
        "danger": "btn-outline-danger",
        "success": "btn-outline-success"
    },
    
    # Brand Colors (Spotify Theme)
    "brand_colors": {
        "primary": "#1DB954",  # Spotify Green
        "secondary": "#535353",
        "success": "#1DB954",
        "info": "#36b9cc",
        "warning": "#f6c23e",
        "danger": "#e74a3b",
        "indigo": "#6610f2",
        "purple": "#6f42c1",
        "pink": "#e83e8c",
        "red": "#e74a3b",
        "orange": "#fd7e14",
        "yellow": "#f6c23e",
        "green": "#1DB954",
        "teal": "#20c9a6",
        "cyan": "#36b9cc",
        "white": "#fff",
        "gray": "#6c757d",
        "gray-dark": "#343a40",
    },
}
# --------------------------------------------------
# Default Primary Key
# --------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

