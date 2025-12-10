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
DEBUG = os.getenv('DEBUG', 'False') == 'True'  # Fixed: Should check for 'True'

# Hosts allowed
ALLOWED_HOSTS = [
    'musiccityug.com',
    'www.musiccityug.com',
    '72.61.200.13',
    'musiccityug.onrender.com',
    '127.0.0.1',
    'localhost',
]

# -----------------------------
# Installed Apps
# -----------------------------
INSTALLED_APPS = [
    'jazzmin',
    'unfold',
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
# Middleware
# -----------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Serve static files efficiently
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
                'music.context_processors.genres',  # Custom context processor
            ],
        },
    },
]

# -----------------------------
# Database (SQLite for dev, switch to PostgreSQL for prod)
# -----------------------------
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
# Static & Media Files
# -----------------------------
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

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
# Email (Dev only)
# -----------------------------
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# -----------------------------
# File Uploads (Larger size for production)
# -----------------------------
# Increased upload limits for large music files
FILE_UPLOAD_MAX_MEMORY_SIZE = 500 * 1024 * 1024  # 500 MB (increased from 200 MB)
DATA_UPLOAD_MAX_MEMORY_SIZE = 500 * 1024 * 1024  # 500 MB (increased from 200 MB)
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000

# NGINX/Apache should handle these, but Django settings as backup
MAX_UPLOAD_SIZE = 500 * 1024 * 1024  # 500 MB
FILE_UPLOAD_PERMISSIONS = 0o644

# -----------------------------
# Session Settings
# -----------------------------
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 1209600  # 2 weeks in seconds
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# -----------------------------
# Security for Production
# -----------------------------
if not DEBUG:
    # Security settings
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    
    # Production database (PostgreSQL - uncomment and configure for production)
    # DATABASES = {
    #     'default': {
    #         'ENGINE': 'django.db.backends.postgresql',
    #         'NAME': os.getenv('DB_NAME', 'sangabiz_db'),
    #         'USER': os.getenv('DB_USER', 'sangabiz_user'),
    #         'PASSWORD': os.getenv('DB_PASSWORD', ''),
    #         'HOST': os.getenv('DB_HOST', 'localhost'),
    #         'PORT': os.getenv('DB_PORT', '5432'),
    #         'CONN_MAX_AGE': 600,  # Connection persistence
    #     }
    # }
    
    # Production email settings
    # EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    # EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
    # EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
    # EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
    # EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
    # EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
    # DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'webmaster@musiccityug.com')
    
    # Logging for production
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'file': {
                'level': 'ERROR',
                'class': 'logging.FileHandler',
                'filename': BASE_DIR / 'logs/django_errors.log',
            },
            'console': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
            },
        },
        'loggers': {
            'django': {
                'handlers': ['file', 'console'],
                'level': 'ERROR',
                'propagate': True,
            },
        },
    }
    
    # Create logs directory if it doesn't exist
    logs_dir = BASE_DIR / 'logs'
    if not logs_dir.exists():
        logs_dir.mkdir(exist_ok=True)
        
else:
    # Development settings
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SECURE_SSL_REDIRECT = False
    SECURE_HSTS_SECONDS = 0

# -----------------------------
# Default Auto Field
# -----------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# -----------------------------
# Jazzmin Admin Settings
# -----------------------------
JAZZMIN_SETTINGS = {
    "site_title": "MusicCityUg Admin",
    "site_header": "MusicCityUg Administration",
    "site_brand": "MusicCityUg",
    "index_title": "Welcome to MusicCityUg Admin",
    "login_logo": None,  # Removed logo from login page
    "login_logo_dark": None,
    "site_logo": "images/logo_small.png",  # Use a smaller logo in admin panel
    "site_logo_classes": "img-circle",
    "welcome_sign": "Welcome to MusicCityUg Admin Panel",
    "copyright": "MusicCityUg Ltd",
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],  # Apps to hide from sidebar
    "hide_models": [],  # Models to hide from sidebar
    
    # Custom icons
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.group": "fas fa-users",
        "accounts.userprofile": "fas fa-user-circle",
        "music": "fas fa-music",
        "music.song": "fas fa-file-audio",
        "music.album": "fas fa-compact-disc",
        "music.genre": "fas fa-tags",
        "artists": "fas fa-microphone-alt",
        "artists.artist": "fas fa-user-tie",
        "library": "fas fa-book",
        "analytics": "fas fa-chart-line",
        "payments": "fas fa-credit-card",
        "help": "fas fa-question-circle",
        "news": "fas fa-newspaper",
    },
    
    # UI tweaks
    "theme": "darkly",
    "show_ui_builder": True,
    
    # Navigation menu
    "topmenu_links": [
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "Website", "url": "/", "new_window": True},
        {"model": "auth.User"},
        {"app": "music"},
        {"app": "artists"},
        {"app": "library"},
    ],
    
    "usermenu_links": [
        {"name": "Support", "url": "https://github.com/farridav/django-jazzmin/issues", "new_window": True, "icon": "fas fa-life-ring"},
        {"model": "auth.user"}
    ],
    
    # Additional security for production admin
    "show_bookmarks": False if not DEBUG else True,
    "related_modal_active": True,
    "custom_css": "css/admin_custom.css" if not DEBUG else None,
    "custom_js": None,
    
    # Performance optimizations
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {"auth.user": "collapsible", "auth.group": "vertical_tabs"},
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
    "sidebar_nav_compact_style": True,
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
    "actions_sticky_top": True,
}

# -----------------------------
# Unfold Admin Settings (Alternative to Jazzmin)
# -----------------------------
UNFOLD = {
    "SITE_TITLE": "MusicCityUg Admin",
    "SITE_HEADER": "MusicCityUg Administration",
    "SITE_URL": "/",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "COLORS": {
        "primary": {
            "50": "250 245 255",
            "100": "243 232 255",
            "200": "233 213 255",
            "300": "216 180 254",
            "400": "192 132 252",
            "500": "168 85 247",
            "600": "147 51 234",
            "700": "126 34 206",
            "800": "107 33 168",
            "900": "88 28 135",
            "950": "59 7 100",
        },
    },
}