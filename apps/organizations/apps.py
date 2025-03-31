# apps/organizations/apps.py

"""
App configuration for the Organizations app.

This module defines the configuration class for the Organizations app,
which manages organizations and their related data.
"""

from django.apps import AppConfig

class OrganizationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.organizations'
    verbose_name = 'Organizations'
