"""
Django settings for sangabiz project.
"""

from pathlib import Path
import os

# -----------------------------
# Base Directory
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# -----------------------------
# Security
# -----------------------------
SECRET_KEY = os.getenv(
    'SECRET_KEY', 
    'django-insecure-p-8cakys+ff2=@ug-r__yilt%sli8bn4%3+hh30+c9$j$=^z*%'
)

# Toggle DEBUG using environment variable (True for dev, False for prod)
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Hosts allowed
ALLOWED_HOSTS = [
    'musiccityug.com',
    'www.musiccityug.com',
    '72.61.200.13',
    'musiccityug.onrender.com',
    '127.0.0.1',
    'localhost',
    '.onrender.com',  # Wildcard for all Render subdomains
]

# -----------------------------
# Installed Apps
# -----------------------------
INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.humanize',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'crispy_bootstrap5',

    # Custom apps
    'accounts',
    'music',
    'artists',
    'analytics',
    'payments',
    'library',
    'help',
    'news',
]

# -----------------------------
# Middleware - CRITICAL ORDER
# -----------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# -----------------------------
# URLs & WSGI
# -----------------------------
ROOT_URLCONF = 'sangabiz.urls'
WSGI_APPLICATION = 'sangabiz.wsgi.application'

# -----------------------------
# Templates
# -----------------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',  # ADD THIS for media files
                'music.context_processors.genres',
            ],
        },
    },
]

# -----------------------------
# Database
# -----------------------------
# Default SQLite for development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# -----------------------------
# Password Validators
# -----------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8},},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# -----------------------------
# Internationalization
# -----------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# -----------------------------
# Static & Media Files - UPDATED FOR PRODUCTION
# -----------------------------
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# WhiteNoise configuration for static files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Ensure media directory exists
os.makedirs(MEDIA_ROOT, exist_ok=True)

# -----------------------------
# Authentication
# -----------------------------
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'

# -----------------------------
# Crispy Forms
# -----------------------------
CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

# -----------------------------
# Email Configuration
# -----------------------------
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# -----------------------------
# File Uploads (Larger size for production)
# -----------------------------
FILE_UPLOAD_MAX_MEMORY_SIZE = 500 * 1024 * 1024  # 500 MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 500 * 1024 * 1024  # 500 MB
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000
MAX_UPLOAD_SIZE = 500 * 1024 * 1024  # 500 MB
FILE_UPLOAD_PERMISSIONS = 0o644

# -----------------------------
# Session Settings
# -----------------------------
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 1209600  # 2 weeks
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# -----------------------------
# Production Settings
# -----------------------------
if not DEBUG:
    # Security settings
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = False  # Set to False for Render.com compatibility
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    
    # PostgreSQL for production (Render.com)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DATABASE_NAME', 'sangabiz_db'),
            'USER': os.getenv('DATABASE_USER', 'sangabiz_user'),
            'PASSWORD': os.getenv('DATABASE_PASSWORD', ''),
            'HOST': os.getenv('DATABASE_HOST', 'localhost'),
            'PORT': os.getenv('DATABASE_PORT', '5432'),
            'CONN_MAX_AGE': 600,
        }
    }
    
    # Logging configuration
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '{levelname} {asctime} {module} {message}',
                'style': '{',
            },
            'simple': {
                'format': '{levelname} {message}',
                'style': '{',
            },
        },
        'handlers': {
            'file': {
                'level': 'ERROR',
                'class': 'logging.FileHandler',
                'filename': BASE_DIR / 'logs/django_errors.log',
                'formatter': 'verbose',
            },
            'console': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                'formatter': 'simple',
            },
        },
        'loggers': {
            'django': {
                'handlers': ['file', 'console'],
                'level': 'ERROR',
                'propagate': True,
            },
            'django.request': {
                'handlers': ['file', 'console'],
                'level': 'ERROR',
                'propagate': False,
            },
        },
    }
    
    # Create logs directory
    logs_dir = BASE_DIR / 'logs'
    if not logs_dir.exists():
        logs_dir.mkdir(exist_ok=True)
        
    # For Render.com, we need to handle media files differently
    # Since Render doesn't persist files, consider using cloud storage
    # For now, we'll serve media files through Django (not recommended for production)
    # Add this to your wsgi.py or asgi.py
    
else:
    # Development settings
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SECURE_SSL_REDIRECT = False
    SECURE_HSTS_SECONDS = 0
    SECURE_PROXY_SSL_HEADER = None

# -----------------------------
# Default Auto Field
# -----------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# -----------------------------
# Jazzmin Admin Settings - UPDATED FOR PRODUCTION
# -----------------------------
JAZZMIN_SETTINGS = {
    "site_title": "MusicCityUg Admin",
    "site_header": "MusicCityUg Administration",
    "site_brand": "MusicCityUg",
    "index_title": "Welcome to MusicCityUg Admin",
    "login_logo": None,  # Disabled to avoid issues
    "login_logo_dark": None,
    "site_logo": None,  # Disabled in production
    "site_logo_classes": "img-circle",
    "welcome_sign": "Welcome to MusicCityUg Admin Panel",
    "copyright": "MusicCityUg Ltd",
    "show_sidebar": True,
    "navigation_expanded": True,
    
    # Icons configuration - using only built-in icons
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.group": "fas fa-users",
        "accounts.UserProfile": "fas fa-user-circle",
        "music.Song": "fas fa-music",
        "music.Album": "fas fa-compact-disc",
        "music.Genre": "fas fa-tag",
        "artists.Artist": "fas fa-microphone",
        "library.Playlist": "fas fa-list",
        "analytics.Visit": "fas fa-chart-line",
        "payments.Transaction": "fas fa-credit-card",
        "help.FAQ": "fas fa-question-circle",
        "news.Article": "fas fa-newspaper",
    },
    
    # UI settings
    "theme": "darkly",
    "show_ui_builder": False,  # Disable in production
    
    # Navigation menu
    "topmenu_links": [
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "View Site", "url": "/", "new_window": True},
        {"model": "auth.User"},
    ],
    
    "usermenu_links": [
        {"name": "View Site", "url": "/", "new_window": True},
        {"model": "auth.user"}
    ],
    
    # Performance optimizations
    "show_bookmarks": False,
    "related_modal_active": False,  # Disable modals for better performance
    "custom_css": None,
    "custom_js": None,
    
    # Layout settings
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {
        "auth.user": "collapsible",
        "auth.group": "vertical_tabs",
    },
    
    # Security
    "actions_sticky_top": True,
    
    # List display settings
    "list_per_page": 25,
}

# -----------------------------
# Jazzmin UI Tweaks
# -----------------------------
JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-dark",
    "accent": "accent-primary",
    "navbar": "navbar-white navbar-light",
    "no_navbar_border": False,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,  # Better for content visibility
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "darkly",
    "dark_mode_theme": "darkly",
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    },
}
