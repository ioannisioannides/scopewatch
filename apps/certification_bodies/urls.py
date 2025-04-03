"""
URL configuration for the Certification Bodies app.

This module defines the URL patterns for the Certification Bodies app,
including routes for listing and viewing details of certification bodies.
"""

from django.urls import path

from . import views

urlpatterns = [
    path(
        "", views.certbody_list_view, name="certbody_list"
    ),  # List view for certification bodies
    path(
        "<int:cb_id>/", views.certbody_detail_view, name="certbody_detail"
    ),  # Detail view for a specific certification body
]
