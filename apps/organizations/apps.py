# apps/organizations/apps.py

"""
App configuration for the Organizations app.
"""

from django.apps import AppConfig


class OrganizationsConfig(AppConfig):
    """
    Configuration class for the Organizations app.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.organizations"
    verbose_name = "Organizations"
