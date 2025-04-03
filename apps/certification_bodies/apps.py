# apps/certification_bodies/apps.py

"""
App configuration for the Certification Bodies app.

This module defines the configuration class for the Certification Bodies app,
which is responsible for managing certification bodies and their related data.
"""

from django.apps import AppConfig


class CertificationBodiesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.certification_bodies"
    verbose_name = "Certification Bodies"
