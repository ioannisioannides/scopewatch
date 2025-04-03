# apps/certification_bodies/admin.py

"""
Admin configuration for the Certification Bodies app.
"""

from django.contrib import admin
from .models import CertBody


@admin.register(CertBody)
class CertBodyAdmin(admin.ModelAdmin):
    """
    Admin interface for the CertBody model.
    """

    list_display = ("name", "accreditation_id", "address", "created_at")  # Ensure fields exist
    search_fields = ("name", "accreditation_id")
