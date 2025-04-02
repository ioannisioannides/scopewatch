"""
URL configuration for the Public app.

This module defines the URL patterns for the Public app,
including routes for the homepage, search, and certificate verification.
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),  # Public homepage
    path('search/', views.search_certified_organizations_view, name='search_certified_organizations'),  # Search page
    path('verify/', views.certificate_verification_view, name='certificate_verification'),  # Certificate verification page
]