"""
URL configuration for the Scopewatch project.
"""

from django.contrib import admin
from django.urls import path, include
from apps.public.views import home_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('audits/', include('apps.audits.urls')),  # Include URLs for the Audits app
    path('certification_bodies/', include('apps.certification_bodies.urls')),  # Include URLs for Certification Bodies app
    path('consultants/', include('apps.consultants.urls')),  # Include URLs for Consultants app
    path('organizations/', include('apps.organizations.urls')),  # Include URLs for Organizations app
    path('', home_view, name='home'),  # Root URL for the public homepage
]
