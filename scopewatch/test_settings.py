"""
Test settings for the Scopewatch project.

These settings are used only for running tests.
"""

from .settings import *  # Import everything from base settings

# Use an in-memory SQLite database for faster tests
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Override the installed apps to break circular dependencies
# Reorder apps to ensure proper dependency resolution
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party apps
    "django_extensions",
    "rest_framework",
    "drf_spectacular",
    "corsheaders",
    # Reordered Scopewatch apps to break circular dependencies
    "apps.organizations",
    "apps.certification_bodies",
    "apps.consultants.apps.ConsultantsConfig",
    "apps.audits.apps.AuditsConfig",
    "apps.public.apps.PublicConfig",
]

# Disable migrations completely for testing
MIGRATION_MODULES = {app.split(".")[-1]: None for app in INSTALLED_APPS}

# Set this to True to avoid time-consuming password hashing
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Use our custom test runner that skips migrations
TEST_RUNNER = "scopewatch.test_runner.NoMigrationsTestRunner"

# Disable all logging during tests
LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "handlers": {
        "null": {
            "class": "logging.NullHandler",
        },
    },
    "loggers": {
        "": {
            "handlers": ["null"],
            "level": "CRITICAL",
        },
    },
}

# Fix template configuration for faster templates
# Don't change APP_DIRS when using loaders
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",  # Global templates directory
        ],
        "APP_DIRS": False,  # Must be False when using loaders
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
            "loaders": [
                (
                    "django.template.loaders.cached.Loader",
                    [
                        "django.template.loaders.filesystem.Loader",
                        "django.template.loaders.app_directories.Loader",
                    ],
                ),
            ],
            "debug": False,
        },
    },
]
