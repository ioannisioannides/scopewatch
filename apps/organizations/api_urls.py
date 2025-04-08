"""
API URL configuration for the Organizations app.

This module defines the URL patterns for the Organizations app's REST API.
"""

from rest_framework.routers import DefaultRouter

from .api_views import OrganizationViewSet, CertificationViewSet

router = DefaultRouter()
router.register(r"organizations", OrganizationViewSet)
router.register(r"certifications", CertificationViewSet)

urlpatterns = router.urls
