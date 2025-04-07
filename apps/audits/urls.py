"""
URL configuration for the Audits app.

This module defines the URL patterns for the Audits app,
including routes for listing and viewing details of audits.
"""

from django.urls import path

from . import views
from .views import debug_view

urlpatterns = [
    path('audit_list', views.audit_list, name='audit_list'),
    path('audit_detail/<int:id>', views.audit_detail, name='audit_detail'),
    path('debug', debug_view, name='debug_view'),
]
