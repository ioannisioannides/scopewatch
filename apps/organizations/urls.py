"""
URL configuration for the Organizations app.

This module defines the URL patterns for the Organizations app,
including routes for listing and viewing details of organizations.
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.organization_list_view, name='organization_list'),  # List view
    path('<int:org_id>/', views.organization_detail_view, name='organization_detail'),  # Detail view
]
