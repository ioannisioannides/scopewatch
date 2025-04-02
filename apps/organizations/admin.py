# apps/organizations/admin.py

from django.contrib import admin

from .models import Organization


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Organization model.
    Adjust list display, search fields, etc., as needed.
    """

    list_display = ("id", "name", "contact_email", "created_at", "is_active")
    search_fields = ("name", "contact_email")
