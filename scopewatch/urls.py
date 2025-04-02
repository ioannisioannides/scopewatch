"""
URL configuration for the Scopewatch project.
"""

from django.contrib import admin
from django.urls import path, include
from apps.public.views import home_view, search_certified_organizations_view, certificate_verification_view  # Import the views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('search/', search_certified_organizations_view, name='search_certified_organizations'),
    path('verify/', certificate_verification_view, name='certificate_verification'),
    path('', home_view, name='home'),  # Root URL
]
