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
DEBUG = os.getenv('DEBUG', 'False') == 'False'

# Hosts allowed
ALLOWED_HOSTS = [
    'musiccityug.com',
    'www.musiccityug.com',
    '72.61.200.13',
    'musiccityug.onrender.com',
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
# File Uploads (Large Songs)
# -----------------------------
FILE_UPLOAD_MAX_MEMORY_SIZE = 200 * 1024 * 1024  # 200 MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 200 * 1024 * 1024  # 200 MB
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000  # optional, for large forms

# -----------------------------
# Security for Production
# -----------------------------
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'DENY'
else:
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SECURE_SSL_REDIRECT = False

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
    "login_logo": "images/logo.jpeg",
    "login_logo_dark": None,
    "site_logo": "images/logo.jpeg",
    "site_logo_classes": "img-circle",
    "welcome_sign": "Welcome to MusicCityUg Admin Panel",
    "copyright": "MusicCityUg Ltd",
    "show_sidebar": True,
    "navigation_expanded": True,
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
    "icons": {
        "auth": "fas fa-users-cog",
        "accounts.userprofile": "fas fa-user-circle",
        "music": "fas fa-music",
        "artists": "fas fa-microphone-alt",
        "library": "fas fa-book",
        "analytics": "fas fa-chart-line",
        "payments": "fas fa-credit-card",
        "help": "fas fa-question-circle",
        "news": "fas fa-newspaper",
    },
    "theme": "darkly",
    "show_ui_builder": True,
}

# -----------------------------
# Jazzmin UI Tweaks (Login Logo Resize)
# -----------------------------
JAZZMIN_UI_TWEAKS = {
    "navbar_fixed": True,
    "sidebar_fixed": True,
    "theme": "darkly",
    "dark_mode_theme": "darkly",
    "login_logo_width": "180px",  # Adjust logo width
    "login_logo_height": "80px",  # Adjust logo height
}

