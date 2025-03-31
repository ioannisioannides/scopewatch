# apps/audits/apps.py

"""
App configuration for the Audits app.

This module defines the configuration class for the Audits app,
which manages audit-related functionality.
"""

from django.apps import AppConfig

class AuditsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.audits'
    verbose_name = 'Audits'
