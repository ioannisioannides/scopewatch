"""
URL configuration for the Scopewatch project.
"""

from django.contrib import admin
from django.urls import include, path

from apps.public.views import (certificate_verification_view, home_view,
                               search_certified_organizations_view)

urlpatterns = [
    path("admin/", admin.site.urls),
    # Include URLs for the Audits app
    path("audits/", include("apps.audits.urls")),
    # Include URLs for Certification Bodies app
    path("certification_bodies/", include("apps.certification_bodies.urls")),
    # Include URLs for Consultants app
    path("consultants/", include("apps.consultants.urls")),
    # Include URLs for Organizations app
    path("organizations/", include("apps.organizations.urls")),
    # Include URLs for the Public app
    path("public/", include("apps.public.urls")),
    path(
        "search/",
        search_certified_organizations_view,
        name="search_certified_organizations",
    ),  # Search page
    path("verify/", certificate_verification_view, name="certificate_verification"),
    # Certificate verification page
    path("", home_view, name="home"),  # Root URL for the public homepage
]
