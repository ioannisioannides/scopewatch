"""
Django settings for the Scopewatch project.

This module contains the settings configuration for the Scopewatch project.
"""

import sys
from pathlib import Path
from decouple import config

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("DJANGO_SECRET_KEY", default="fallback-secret-key")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config("DEBUG", default=False, cast=bool)

# Custom test runner to skip migrations during testing
TEST_RUNNER = "scopewatch.test_runner.NoMigrationsTestRunner"

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "testserver"]

# Security settings for production
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# By default, enable SSL redirect in production
SECURE_SSL_REDIRECT = True

# Disable SSL redirection during testing
# The test runner activates the 'test' in sys.argv
if "test" in sys.argv or "pytest" in sys.modules or DEBUG:
    print("Test environment detected - disabling SSL redirect")
    SECURE_SSL_REDIRECT = False
    # Disable all security redirects during testing
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    # Keep URL patterns consistent
    APPEND_SLASH = False
else:
    # Security for production environments
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    # This is the key setting that causes the URL trailing slash issues
    # For consistency, we'll set it to False and update our URL patterns
    APPEND_SLASH = False

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Scopewatch apps
    "apps.audits.apps.AuditsConfig",
    "apps.certification_bodies",
    "apps.organizations",
    "apps.consultants.apps.ConsultantsConfig",
    "apps.public.apps.PublicConfig",
    # Third-party apps
    "django_extensions",
    "rest_framework",
    "drf_spectacular",
    "corsheaders",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",  # CORS middleware
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# CORS configuration
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # For React frontend
    "http://localhost:8000",
]

ROOT_URLCONF = "scopewatch.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",  # Global templates directory
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "scopewatch.wsgi.application"
ASGI_APPLICATION = "scopewatch.asgi.application"

# REST Framework settings
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
}

# Spectacular API documentation settings
SPECTACULAR_SETTINGS = {
    "TITLE": "Scopewatch API",
    "DESCRIPTION": "API for Scopewatch compliance management platform",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME", default="scopewatch"),
        "USER": config("DB_USER", default="scopewatch_user"),
        "PASSWORD": config("DB_PASSWORD", default=""),
        "HOST": config("DB_HOST", default="127.0.0.1"),
        "PORT": config("DB_PORT", default="5432"),
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"  # Directory to collect static files

# Media files (user uploads)
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Redirect URLs after login/logout
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Logging configuration
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "logs" / "django.log",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
