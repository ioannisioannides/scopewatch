"""
URL configuration for the Consultants app.

This module defines the URL patterns for the Consultants app,
including routes for listing consultants and consultancy firms.
"""

from django.urls import path
from . import views

urlpatterns = [
    path(
        'consultants/',
        views.consultant_list_view,
        name='consultant_list'
    ),  # List view for consultants
    path(
        'firms/',
        views.consultancy_firm_list_view,
        name='consultancy_firm_list'
    ),  # List view for consultancy firms
]