# apps/consultants/admin.py

from django.contrib import admin

from .models import ConsultancyFirm, Consultant, ConsultantDocument


@admin.register(Consultant)
class ConsultantAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Consultant model.
    """

    list_display = ("id", "user", "specialties", "experience_years")
    search_fields = ("user__username", "specialties")


@admin.register(ConsultancyFirm)
class ConsultancyFirmAdmin(admin.ModelAdmin):
    """
    Admin configuration for the ConsultancyFirm model.
    """

    list_display = ("id", "name", "address", "website")
    search_fields = ("name",)


@admin.register(ConsultantDocument)
class ConsultantDocumentAdmin(admin.ModelAdmin):
    """
    Admin interface for ConsultantDocument model.
    """

    list_display = (
        "title",
        "consultant",
        "organization",
        "document_type",
        "standard",
        "status",
    )
    list_filter = ("document_type", "standard", "status", "created_at")
    search_fields = (
        "title",
        "consultant__user__username",
        "organization__name",
        "standard",
    )
    raw_id_fields = ("consultant", "organization", "engagement")
    date_hierarchy = "created_at"
