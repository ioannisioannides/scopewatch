"""
URL configuration for the Certification Bodies app.

This module defines the URL patterns for the Certification Bodies app,
including routes for listing and viewing details of certification bodies,
as well as audit decisions and certificate issuance.
"""

from django.urls import path

from . import views

app_name = "certification_bodies"

urlpatterns = [
    # Dashboard view
    path("dashboard/", views.cert_body_dashboard, name="dashboard"),
    path("", views.certbody_list_view, name="certbody_list"),  # List view for certification bodies
    path(
        "<int:cb_id>", views.certbody_detail_view, name="certbody_detail"
    ),  # Detail view for a specific certification body
    # Audit decision views
    path(
        "audits/pending/",
        views.AuditPendingDecisionListView.as_view(),
        name="pending_decisions",
    ),
    path(
        "audits/<int:audit_id>/decision/",
        views.audit_decision_view,
        name="audit_decision",
    ),
    path(
        "audits/<int:audit_id>/certificate/",
        views.issue_certificate_view,
        name="issue_certificate",
    ),
]
