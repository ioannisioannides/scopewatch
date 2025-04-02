"""
URL configuration for the Scopewatch project.
"""

from django.contrib import admin
from django.urls import path, include
from apps.public.views import home_view, search_certified_organizations_view  # Import the views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('audits/', include('apps.audits.urls')),
    path('certification_bodies/', include('apps.certification_bodies.urls')),
    path('organizations/', include('apps.organizations.urls')),
    path('', home_view, name='home'),  # Root URL
    path('search/', search_certified_organizations_view, name='search_certified_organizations'),
    path('login/', include('django.contrib.auth.urls')),  # Built-in login/logout views
]
