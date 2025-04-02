# apps/organizations/views.py

"""
Views for the Organizations app.

This module contains views for listing organizations and displaying organization details.
"""

from django.shortcuts import get_object_or_404, render

from .models import Organization


def organization_list_view(request):
    """
    View for listing all organizations.
    """
    organizations = Organization.objects.all()
    return render(request, 'organizations/organization_list.html', {'organizations': organizations})

def organization_detail_view(request, org_id):
    """
    View for displaying the details of a specific organization.
    """
    organization = get_object_or_404(Organization, id=org_id)
    return render(request, 'organizations/organization_detail.html', {'organization': organization})
