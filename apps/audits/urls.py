"""
URL configuration for the Audits app.

This module defines the URL patterns for the Audits app,
including routes for listing and viewing details of audits.
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.audit_list_view, name='audit_list'),  # List view for audits
    path('<int:audit_id>/', views.audit_detail_view, name='audit_detail'),  # Detail view for a specific audit
]
