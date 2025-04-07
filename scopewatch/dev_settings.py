"""
Django development settings for the Scopewatch project.

This module contains development-specific settings and imports the base settings.
"""

from .settings import *  # noqa

# Override production settings for development
DEBUG = True
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Use SQLite for development if preferred
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

# Add Django Debug Toolbar for development
INSTALLED_APPS += ['debug_toolbar']  # noqa
MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE  # noqa

# Internal IPs for Django Debug Toolbar
INTERNAL_IPS = ['127.0.0.1']

# Email backend for development (prints to console instead of sending)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'