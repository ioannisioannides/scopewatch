# apps/audits/admin.py

from django.contrib import admin

from .models import Audit


@admin.register(Audit)
class AuditAdmin(admin.ModelAdmin):
    """
    Admin configuration for Audit model.
    Adjust list display, search fields, etc. as needed.
    """

    list_display = (
        "id",
        "audit_type",
        "organization",
        "certbody",
        "start_date",
        "end_date",
    )
    search_fields = ("audit_type",)
