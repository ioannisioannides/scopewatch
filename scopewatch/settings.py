"""
Django settings for the Scopewatch project.

This module contains the settings configuration for the Scopewatch project.
"""

import sys
from pathlib import Path

# Import our custom config module instead of using decouple directly
from scopewatch.config import (
    config, 
    is_debug_mode, 
    is_test_environment, 
    is_production,
    is_development
)

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
# In production, this will raise an error if the environment variable is not set
if is_production():
    # In production, SECRET_KEY is absolutely required
    SECRET_KEY = config("DJANGO_SECRET_KEY", required=True)
else:
    # In development/test, allow a fallback for convenience
    SECRET_KEY = config("DJANGO_SECRET_KEY", default="dev-only-insecure-key-do-not-use-in-production")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = is_debug_mode()

# Custom test runner to skip migrations during testing
TEST_RUNNER = "scopewatch.test_runner.NoMigrationsTestRunner"

# Add required environment-specific hosts
ADDITIONAL_HOSTS = config("ADDITIONAL_HOSTS", default="", cast=str).split(",") if config("ADDITIONAL_HOSTS", default="") else []
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "testserver"] + ADDITIONAL_HOSTS

# Security settings for production
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# By default, enable SSL redirect in production
SECURE_SSL_REDIRECT = is_production()

# Security settings based on environment
if is_development() or is_test_environment():
    # Disable all security redirects during testing/development
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
else:
    # Security for production environments
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# URL handling - consistent behavior with APPEND_SLASH=True
# This avoids URL resolution inconsistencies
APPEND_SLASH = True

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
    "apps.certification_bodies.apps.CertificationBodiesConfig",
    "apps.organizations.apps.OrganizationsConfig",
    "apps.consultants.apps.ConsultantsConfig",
    "apps.public.apps.PublicConfig",
    "apps.management.apps.ManagementConfig",  # Updated to use proper AppConfig
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
    # Custom middleware
    "apps.management.middleware.SQLiteOptimizedConnectionMiddleware",  # SQLite optimization
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

# Database configuration
# Default to SQLite, but allow override through environment variables
DB_ENGINE = config("DB_ENGINE", default="django.db.backends.sqlite3")

if DB_ENGINE == "django.db.backends.sqlite3":
    DATABASES = {
        "default": {
            "ENGINE": DB_ENGINE,
            "NAME": BASE_DIR / "db.sqlite3",
            # SQLite optimizations - removed incompatible parameters for Python 3.13
            "OPTIONS": {
                "timeout": 20,  # Busy timeout in seconds
                "isolation_level": None,  # Use autocommit mode
            },
            "ATOMIC_REQUESTS": True,  # Wrap each HTTP request in a transaction
        }
    }
else:
    # PostgreSQL or other database engine
    DATABASES = {
        "default": {
            "ENGINE": DB_ENGINE,
            "NAME": config("DB_NAME", required=True),
            "USER": config("DB_USER", required=True),
            "PASSWORD": config("DB_PASSWORD", required=True),
            "HOST": config("DB_HOST", default="localhost"),
            "PORT": config("DB_PORT", default="5432"),
            "ATOMIC_REQUESTS": True,
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
