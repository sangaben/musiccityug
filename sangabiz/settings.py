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

DEBUG = False

ALLOWED_HOSTS = [
    "musiccityug.com",
    "www.musiccityug.com",
    "sangabiz.com",
    "www.sangabiz.com",
    "31.220.78.100",
    "127.0.0.1",
    "localhost",
    ".da.direct", 
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
# Jazzmin Configuration (App-Specific Search)
# --------------------------------------------------
SITE_URL = "https://musiccityug.com"

JAZZMIN_SETTINGS = {
    # ========== BRANDING & THEME ==========
    "site_title": "MusicCityUG Admin",
    "site_header": "MusicCityUG",
    "site_brand": "MusicCityUG",
    "site_logo": "images/logo.jpeg",
    "login_logo": "images/llogo.jpeg",
    "site_icon": "images/favicon.ico",
    "login_logo_dark": "images/logo.jpeg",
    "welcome_sign": "Welcome to MusicCityUG Administration",
    "copyright": "© 2025 MusicCityUG | Uganda's Sound, Your Playlist",
    
    # ========== THEME & UI ==========
    "theme": "darkly",
    "dark_mode_theme": "darkly",
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    "order_with_respect_to": [
        "music", "artists", "accounts", "payments", 
        "analytics", "library", "news", "help", "auth"
    ],
    
    # ========== REMOVE GLOBAL SEARCH ==========
    "search_model": [],  # Empty list removes the global search bar
    
    # ========== TOP MENU ==========
    "topmenu_links": [
        {"name": "Dashboard", "url": "admin:index", "permissions": ["auth.view_user"], "icon": "fas fa-tachometer-alt"},
        {"name": "Visit Website", "url": SITE_URL, "new_window": True, "icon": "fas fa-globe"},
        {"model": "auth.user", "icon": "fas fa-users"},
    ],
    
    # ========== USER MENU ==========
    "usermenu_links": [
        {"name": "MusicCityUG", "url": SITE_URL, "new_window": True, "icon": "fas fa-globe"},
        {"name": "Support", "icon": "fas fa-question-circle"},
        {"model": "auth.user", "icon": "fas fa-user"},
    ],
    
    # ========== ICONS ==========
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "music": "fas fa-music",
        "music.Song": "fas fa-file-audio",
        "music.Genre": "fas fa-tag",
        "music.SongPlay": "fas fa-play-circle",
        "music.SongDownload": "fas fa-download",
        "artists": "fas fa-microphone-alt",
        "artists.Artist": "fas fa-user-tie",
        "artists.Band": "fas fa-users",
        "accounts": "fas fa-user-circle",
        "accounts.UserProfile": "fas fa-id-card",
        "payments": "fas fa-credit-card",
        "payments.Transaction": "fas fa-exchange-alt",
        "payments.Subscription": "fas fa-calendar-check",
        "analytics": "fas fa-chart-line",
        "analytics.PlayAnalytic": "fas fa-chart-bar",
        "analytics.DownloadAnalytic": "fas fa-chart-pie",
        "library": "fas fa-book",
        "library.Collection": "fas fa-folder",
        "help": "fas fa-question-circle",
        "help.FAQ": "fas fa-comment-dots",
        "help.SupportTicket": "fas fa-ticket-alt",
        "news": "fas fa-newspaper",
        "news.Article": "fas fa-file-alt",
        "news.Category": "fas fa-folder",
    },
    
    # ========== CUSTOM ACTIONS ==========
    "custom_links": {
        "music": [
            {
                "name": "Bulk Upload",
                "url": "/admin/music/song/bulk-upload/",
                "icon": "fas fa-upload",
                "permissions": ["music.add_song"]
            },
            {
                "name": "Quick Stats",
                "url": "/admin/music/quick-stats/",
                "icon": "fas fa-chart-pie",
                "permissions": ["music.view_song"]
            }
        ],
        "artists": [
            {
                "name": "Featured Artists",
                "url": "/admin/artists/featured/",
                "icon": "fas fa-star",
                "permissions": ["artists.view_artist"]
            },
            {
                "name": "Artist Analytics",
                "url": "/admin/artists/analytics/",
                "icon": "fas fa-chart-line",
                "permissions": ["artists.view_artist"]
            }
        ],
    },
    
    # ========== UI SETTINGS ==========
    "show_ui_builder": False,
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {
        "auth.user": "collapsible",
        "auth.group": "vertical_tabs",
    },
    "related_modal_active": False,
    
    # ========== DASHBOARD ==========
    "show_dashboard_stats": True,
    
    # ========== IMPORTANT: DISABLE GLOBAL SEARCH UI ==========
    "show_changelist_search": False,
    
    # Header specific fixes
    "navbar_fixed": True,
    "navbar_small_text": False,
    
    # Sidebar fixes
    "sidebar_fixed": True,
    "sidebar_nav_small_text": False,
    "sidebar_nav_child_indent": False,
    
    # Custom CSS/JS for app-specific search
    "custom_css": "admin/css/app_search.css",
    "custom_js": "admin/js/app_search.js",
}

JAZZMIN_UI_TWEAKS = {
    "theme": "darkly",
    "dark_mode_theme": "darkly",
    "navbar": "navbar-dark",
    "navbar_fixed": True,
    "sidebar": "sidebar-dark-primary",
    "sidebar_fixed": True,
    "footer_fixed": False,
    "actions_sticky_top": False,
}
# --------------------------------------------------
# Default Primary Key
# --------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

