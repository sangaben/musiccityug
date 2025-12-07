"""
Django settings for sangabiz project.
"""

from pathlib import Path
import os
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-p-8cakys+ff2=@ug-r__yilt%sli8bn4%3+hh30+c9$j$=^z*%')
DEBUG = os.getenv('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = ['.onrender.com', 'localhost', '127.0.0.1', '0.0.0.0']

INSTALLED_APPS = [
    # Unfold Admin - MUST be before django.contrib.admin
    'unfold',
    'unfold.contrib.filters',
    'unfold.contrib.forms',
    'unfold.contrib.import_export',
    
    # Django core apps
    'django.contrib.humanize',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',
    
    # Third-party apps
    'crispy_forms',
    'crispy_bootstrap5',
    'import_export',
    
    # Custom apps
    'accounts',
    'music',
    'artists', 
    'analytics',
    'payments',
    'library',
]

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

ROOT_URLCONF = 'sangabiz.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'music.context_processors.genres',
            ],
        },
    },
]

WSGI_APPLICATION = 'sangabiz.wsgi.application'

# Database - PostgreSQL for production, SQLite for local development
if DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': dj_database_url.config(
            default=os.getenv('DATABASE_URL'),
            conn_max_age=600,
            conn_health_checks=True,
        )
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Media files (uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Authentication
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Email settings
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
    EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
    EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
    EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
    EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB

# Security settings
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_SSL_REDIRECT = not DEBUG

if not DEBUG:
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'DENY'

# WhiteNoise configuration
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Unfold Admin Configuration
UNFOLD = {
    "SITE_TITLE": "MusicCityUg Admin",
    "SITE_HEADER": "MusicCityUg Administration",
    "SITE_URL": "/",
    "SITE_ICON": {
        "light": "logo-light.png",  # light mode
        "dark": "logo-dark.png",   # dark mode
    },
    "SITE_LOGO": {
        "light": "logo-light.png",
        "dark": "logo-dark.png",
    },
    "SITE_SYMBOL": "music_note",  # Material icon name
    "SITE_FAVICONS": [
        {
            "rel": "icon",
            "sizes": "32x32",
            "type": "image/png",
            "href": "/static/favicon-32x32.png",
        },
    ],
    "SHOW_HISTORY": True,  # show object history
    "SHOW_VIEW_ON_SITE": True,  # show "view on site" button
    "ENVIRONMENT": "sangabiz.utils.environment_callback",
    "DASHBOARD_CALLBACK": "sangabiz.views.dashboard_callback",
    "THEME": "dark",  # Force dark theme: "light", "dark" or "auto"
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
    "EXTENSIONS": {
        "modeltranslation": {
            "flags": {
                "en": "🇺🇸",
                "fr": "🇫🇷",
                "nl": "🇳🇱",
            },
        },
    },
    "SIDEBAR": {
        "show_search": True,  # Search in applications and models
        "show_all_applications": True,  # Show all applications
        "navigation": [
            {
                "title": "Music Management",
                "separator": True,
                "items": [
                    {
                        "title": "Dashboard",
                        "icon": "dashboard",
                        "link": "/admin/",
                    },
                    {
                        "title": "Songs",
                        "icon": "library_music",
                        "link": "/admin/music/song/",
                    },
                    {
                        "title": "Artists",
                        "icon": "person",
                        "link": "/admin/artists/artist/",
                    },
                    {
                        "title": "Albums",
                        "icon": "album",
                        "link": "/admin/music/album/",
                    },
                    {
                        "title": "Genres",
                        "icon": "category",
                        "link": "/admin/music/genre/",
                    },
                ],
            },
            {
                "title": "User Management",
                "separator": True,
                "items": [
                    {
                        "title": "Users",
                        "icon": "people",
                        "link": "/admin/accounts/user/",
                    },
                    {
                        "title": "User Profiles",
                        "icon": "account_circle",
                        "link": "/admin/accounts/userprofile/",
                    },
                ],
            },
            {
                "title": "Business",
                "separator": True,
                "items": [
                    {
                        "title": "Payments",
                        "icon": "payments",
                        "link": "/admin/payments/payment/",
                    },
                    {
                        "title": "Subscriptions",
                        "icon": "subscriptions",
                        "link": "/admin/payments/subscription/",
                    },
                    {
                        "title": "Analytics",
                        "icon": "analytics",
                        "link": "/admin/analytics/useractivity/",
                    },
                ],
            },
            {
                "title": "Library",
                "separator": True,
                "items": [
                    {
                        "title": "Playlists",
                        "icon": "playlist_play",
                        "link": "/admin/library/playlist/",
                    },
                    {
                        "title": "Favorites",
                        "icon": "favorite",
                        "link": "/admin/library/favorite/",
                    },
                ],
            },
        ],
    },
    "TABS": [
        {
            "models": [
                "music.song",
                "music.album",
                "music.genre",
            ],
            "items": [
                {
                    "title": "Music",
                    "icon": "music_note",
                },
            ],
        },
        {
            "models": [
                "accounts.user",
                "accounts.userprofile",
            ],
            "items": [
                {
                    "title": "Users",
                    "icon": "people",
                },
            ],
        },
    ],
}

# Unfold CSS/JS overrides
UNFOLD["STYLES"] = [
    "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap",
]

UNFOLD["SCRIPTS"] = [
    "https://cdn.jsdelivr.net/npm/chart.js@4.3.0/dist/chart.umd.min.js",
]

# Optional: Custom admin site header
ADMIN_SITE_HEADER = "MusicCityUg Administration"
ADMIN_SITE_TITLE = "MusicCityUg Admin Portal"
ADMIN_INDEX_TITLE = "Welcome to MusicCityUg Admin"