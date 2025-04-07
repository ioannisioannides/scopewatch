"""
Main API URL configuration for the Scopewatch project.

This module integrates all app-specific API URL configurations and
adds API documentation endpoints.
"""

from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework import routers

# Create a default router for the overall API
router = routers.DefaultRouter()

# API URLs
urlpatterns = [
    # Include app-specific API endpoints
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('organizations/', include('apps.organizations.api_urls')),
    
    # API schema and documentation endpoints
    path('schema', SpectacularAPIView.as_view(), name='schema'),
    path('schema/swagger-ui', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('schema/redoc', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]