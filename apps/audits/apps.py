# apps/audits/apps.py

"""
App configuration for the Audits app.
"""

from django.apps import AppConfig


class AuditsConfig(AppConfig):
"""
    Configuration class for the Audits app.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.audits"
    verbose_name = "Audits"
