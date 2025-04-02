"""
URL configuration for the Audits app.

This module defines the URL patterns for the Audits app,
including routes for listing and viewing details of audits.
"""

from django.contrib import admin
from django.urls import path, include
from apps.public.views import home_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('audits/', include('apps.audits.urls')),
    path('certification_bodies/', include('apps.certification_bodies.urls')),
    path('consultants/', include('apps.consultants.urls')),
    path('organizations/', include('apps.organizations.urls')),
    path('', home_view, name='home'),
]
