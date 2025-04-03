# apps/organizations/admin.py

"""
Admin configuration for the Organizations app.
"""

from django.contrib import admin

from .models import Organization


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    """
    Admin interface for the Organization model.
    """

    list_display = ("name", "contact_email")
