# apps/audits/admin.py

from django.contrib import admin

from .models import Audit, AuditTeam, AuditorAssignment, NonConformance, DocumentSubmission, AuditResult


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


@admin.register(DocumentSubmission)
class DocumentSubmissionAdmin(admin.ModelAdmin):
    """
    Admin interface for DocumentSubmission model.
    """
    list_display = ('title', 'audit', 'submitted_by', 'submitted_at', 'status')
    list_filter = ('status', 'document_type', 'submitted_at')
    search_fields = ('title', 'audit__organization__name', 'submitted_by__username')
    raw_id_fields = ('audit', 'submitted_by', 'consultant')
    date_hierarchy = 'submitted_at'


@admin.register(AuditResult)
class AuditResultAdmin(admin.ModelAdmin):
    """
    Admin interface for AuditResult model.
    """
    list_display = ('audit', 'decision', 'decision_date', 'nonconformances_closed', 'recommendation')
    list_filter = ('decision', 'decision_date', 'nonconformances_closed')
    search_fields = ('audit__organization__name', 'notes')
    raw_id_fields = ('audit', 'decided_by')
    date_hierarchy = 'decision_date'
    
    def get_readonly_fields(self, request, obj=None):
        """
        Make audit field readonly when editing an existing object.
        """
        if obj:  # editing an existing object
            return self.readonly_fields + ('audit',)
        return self.readonly_fields
