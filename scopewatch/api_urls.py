"""
API URL configuration for the Scopewatch project.

This module defines the URL patterns for the API endpoints of the Scopewatch project.
"""

from django.http import JsonResponse
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter


# Setup dummy view for API documentation
@api_view(["GET"])
def api_root(request):
    """
    API root view.
    This endpoint serves as the API entry point with links to available resources.
    """
    return Response(
        {
            "message": "Welcome to ScopeWatch API",
            "version": "1.0",
            "status": "API is under development",
        }
    )


# API URL patterns
urlpatterns = [
    # API documentation schema
    path("schema", SpectacularAPIView.as_view(), name="schema"),
    path(
        "schema/swagger",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("schema/redoc", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    # API root entry point
    path("", api_root, name="api-root"),
    # Include the auth URLs with a unique namespace
    path("auth/", include("rest_framework.urls", namespace="api_rest_framework")),
    # Include default DRF browsable API with a different namespace
    path("api-auth/", include("rest_framework.urls", namespace="browsable_api")),
]

# Add a comment explaining the current state of the API implementation
"""
# Future API endpoints will be organized by app:
# - /organizations/ - Organizations and certifications endpoints
# - /certification_bodies/ - Certification bodies and auditors endpoints
# - /consultants/ - Consultants and consultancy firms endpoints
# - /audits/ - Audits, audit teams, and nonconformances endpoints

# Example router setup (commented out until API views are implemented):
# router = DefaultRouter(trailing_slash=False)
# router.register(r'organizations', OrganizationViewSet)
# router.register(r'certifications', CertificationViewSet)
# router.register(r'certbodies', CertBodyViewSet)
# router.register(r'auditors', AuditorViewSet)
# router.register(r'consultants', ConsultantViewSet)
# router.register(r'consultancy-firms', ConsultancyFirmViewSet)
# router.register(r'audits', AuditViewSet)
# urlpatterns += [path('', include(router.urls))]
"""
