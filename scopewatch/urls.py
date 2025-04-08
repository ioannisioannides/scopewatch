"""
URL configuration for the Scopewatch project.
"""

from django.contrib import admin
from django.urls import include, path
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.urls import reverse

from apps.public.views import (certificate_verification_view, home_view,
                               search_certified_organizations_view)

def index(request):
    return HttpResponse("Welcome to Scopewatch!")

urlpatterns = [
    path("admin", admin.site.urls),
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
    # Include the public app URLs
    path("verify/", include("apps.public.urls")),
    
    # API URLs
    path("api/v1/", include("scopewatch.api_urls")),
    
    # Direct view mappings 
    path("search", search_certified_organizations_view, name="search_certified_organizations"),
    path("verify", certificate_verification_view, name="certificate_verification"),
    path("", home_view, name="home"),  # Root URL for the public homepage
    path("index", index, name="index"),  # Index page
    
    # Non-namespaced URL patterns for certification bodies
    path("certbody/<int:cb_id>", lambda request, cb_id: redirect(
        reverse("certification_bodies:certbody_detail", args=[cb_id])), 
        name="certbody_detail"
    ),
    path("certbody", lambda request: redirect(
        reverse("certification_bodies:certbody_list")), 
        name="certbody_list"
    ),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
