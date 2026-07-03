import os
from pathlib import Path
import environ
import dj_database_url

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Initialize environment variables
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

# Initialize environment variables
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Core settings
SECRET_KEY = env("SECRET_KEY", default="super-secret-key")
DEBUG = env.bool("DEBUG", default=True)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["*"])

# Installed apps
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party apps
    "rest_framework",
    "rest_framework_simplejwt",
    # Local apps
    "apps.core",
    "apps.users",
    "apps.communities",
    "apps.projects",
    "apps.locations",
    "apps.socialroles",
    "apps.maladaptives",
    "apps.metacrisis_facets",
    "apps.capitals",
    "apps.bioregions",
    "apps.challenges",
    "apps.meetings",
    "apps.relationships",
    "apps.resolutions",
    "apps.tasks",
    "apps.acl",
    "apps.stories",
    "apps.bookmarks",
    "apps.utils",
    "apps.api",
    # Megachart knowledge graph system
    "apps.megachart",
]

# Custom user model
AUTH_USER_MODEL = "users.User"

# Middleware
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

# URL configuration
ROOT_URLCONF = "config.urls"

# Templates
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(BASE_DIR, "templates"),
            os.path.join(BASE_DIR, "apps", "pages", "templates"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "config.context_processors.site_settings",
                "apps.users.context_processors.registration_mode",
            ],
        },
    },
]

# WSGI
WSGI_APPLICATION = "config.wsgi.application"


# Database
# Determine the database URL based on RUN_MODE
if env("RUN_MODE") == "local":
    DATABASE_URL = env("LOCAL_DATABASE_URL")
else:
    DATABASE_URL = env("CPANEL_DATABASE_URL")

DATABASES = {
    "default": dj_database_url.config(default=DATABASE_URL),
}

print("DATABASE_URL loaded:", env("DATABASE_URL", default=None))

# Password validation (simplified for dev)
AUTH_PASSWORD_VALIDATORS = []

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = "/static/"
if env("RUN_MODE") == "local":
    STATIC_ROOT = os.path.join(BASE_DIR, "/static")
else:
    STATIC_ROOT = os.path.join(BASE_DIR, "../public_html/static")

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

# Media files
MEDIA_URL = "/media/"

if env("RUN_MODE") == "local":
    MEDIA_ROOT = os.path.join(BASE_DIR, "media")
else:
    MEDIA_ROOT = os.path.join(BASE_DIR, "../public_html/media")


# WhiteNoise configuration
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
WHITENOISE_USE_FINDERS = True
WHITENOISE_MANIFEST_STRICT = False
WHITENOISE_ALLOW_ALL_ORIGINS = True

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Authentication settings
LOGIN_URL = "login"

# Django REST Framework settings
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",  # For browsable API
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 100,
}

# JWT settings
from datetime import timedelta

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": False,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
}

# Add URL_OVERRIDE setting for local testing
URL_OVERRIDE = env("URL_OVERRIDE", default=None)

# Registration mode settings
# Options: 'open' (anyone can sign up), 'approval' (sign up requires approval), 'closed' (only admins can create users)
REGISTRATION_MODE = env("REGISTRATION_MODE", default="open")

# Google OAuth settings
GOOGLE_OAUTH_CLIENT_ID = env("GOOGLE_OAUTH_CLIENT_ID", default="")
GOOGLE_OAUTH_CLIENT_SECRET = env("GOOGLE_OAUTH_CLIENT_SECRET", default="")
GOOGLE_OAUTH_ENCRYPTION_KEY = env("GOOGLE_OAUTH_ENCRYPTION_KEY", default="")

# Google Analytics
GOOGLE_ANALYTICS_ID = env("GOOGLE_ANALYTICS_ID", default="")

# Tile cache settings (short-lived, bounded in-memory cache)
MAP_TILE_CACHE_TIMEOUT = env.int("MAP_TILE_CACHE_TIMEOUT", default=900)
MAP_TILE_CACHE_MAX_ENTRIES = env.int("MAP_TILE_CACHE_MAX_ENTRIES", default=2000)

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "mycelium-default-cache",
    },
    "tiles": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "mycelium-tile-cache",
        "TIMEOUT": MAP_TILE_CACHE_TIMEOUT,
        "OPTIONS": {
            "MAX_ENTRIES": MAP_TILE_CACHE_MAX_ENTRIES,
            "CULL_FREQUENCY": 3,
        },
    },
}
