# apps/consultants/apps.py

"""
App configuration for the Consultants app.

This module defines the configuration class for the Consultants app,
which manages consultants and consultancy firms.
"""

from django.apps import AppConfig


class ConsultantsConfig(AppConfig):
    """
    Configuration class for the Consultants app.

    This class sets the default primary key field type and specifies
    the app name and verbose name for the Consultants app.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.consultants"
    verbose_name = "Consultants"
