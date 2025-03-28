# apps/certification_bodies/admin.py

from django.contrib import admin
from .models import CertBody

@admin.register(CertBody)
class CertBodyAdmin(admin.ModelAdmin):
    """
    Admin configuration for the CertBody model.
    Adjust list display, filters, etc., as needed.
    """
    list_display = ('id', 'name', 'accreditation_id', 'address', 'created_at')
    search_fields = ('name', 'accreditation_id')
