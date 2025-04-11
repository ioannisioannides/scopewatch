# apps/certification_bodies/admin.py

"""
Admin configuration for the Certification Bodies app.
"""

from django.contrib import admin

from .models import Auditor, CertBody, StandardQualification


@admin.register(CertBody)
class CertBodyAdmin(admin.ModelAdmin):
    """
    Admin interface for the CertBody model.
    """

    list_display = (
        "name",
        "accreditation_id",
        "address",
        "created_at",
    )  # Ensure fields exist
    search_fields = ("name", "accreditation_id")


@admin.register(Auditor)
class AuditorAdmin(admin.ModelAdmin):
    """
    Admin interface for Auditor model.
    """

    list_display = ("user", "specialties", "is_active")
    list_filter = ("is_active", "cert_bodies")
    search_fields = ("user__username", "user__email", "specialties")
    filter_horizontal = ("cert_bodies",)
    raw_id_fields = ("user",)


@admin.register(StandardQualification)
class StandardQualificationAdmin(admin.ModelAdmin):
    """
    Admin interface for StandardQualification model.
    """

    list_display = (
        "auditor",
        "standard",
        "cert_body",
        "qualification_date",
        "expiry_date",
        "is_valid",
    )
    list_filter = ("standard", "cert_body", "qualification_date")
    search_fields = ("auditor__user__username", "standard", "cert_body__name")
    raw_id_fields = ("auditor", "cert_body")
    date_hierarchy = "qualification_date"
