"""
URL configuration for the Scopewatch project.
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('audits/', include('apps.audits.urls')),
    path('certification_bodies/', include('apps.certification_bodies.urls')),
    path('organizations/', include('apps.organizations.urls')),
]
