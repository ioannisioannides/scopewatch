# apps/public/apps.py

"""
App configuration for the Public app.

This module defines the configuration class for the Public app,
which provides public-facing functionality such as certificate verification.
"""

from django.apps import AppConfig


class PublicConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.public"
    verbose_name = "Public"
