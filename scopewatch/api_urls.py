"""
API URL configuration for the Scopewatch project.

This module defines the URL patterns for the API endpoints of the Scopewatch project.
"""

from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter

# Import API views here
from apps.organizations.api.views import OrganizationViewSet, CertificationViewSet
from apps.certification_bodies.api.views import CertBodyViewSet, AuditorViewSet
from apps.consultants.api.views import ConsultantViewSet, ConsultancyFirmViewSet
from apps.audits.api.views import AuditViewSet

# API routers
router = DefaultRouter(trailing_slash=False)  # Configure router without trailing slashes
router.register(r'organizations', OrganizationViewSet)
router.register(r'certifications', CertificationViewSet)
router.register(r'certbodies', CertBodyViewSet)
router.register(r'auditors', AuditorViewSet)
router.register(r'consultants', ConsultantViewSet)
router.register(r'consultancy-firms', ConsultancyFirmViewSet)
router.register(r'audits', AuditViewSet)

# API URL patterns
urlpatterns = [
    # API schema and documentation
    path('schema', SpectacularAPIView.as_view(), name='schema'),
    path('schema/swagger', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('schema/redoc', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # Include API endpoints from router
    path('', include(router.urls)),
]