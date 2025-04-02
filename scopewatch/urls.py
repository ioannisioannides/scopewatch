"""
URL configuration for the Scopewatch project.
"""

from django.contrib import admin
from django.urls import path, include
from apps.public.views import home_view  # Import the root view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('audits/', include('apps.audits.urls')),
    path('certification_bodies/', include('apps.certification_bodies.urls')),
    path('organizations/', include('apps.organizations.urls')),
    path('', home_view, name='home'),  # Add the root URL pattern
]
