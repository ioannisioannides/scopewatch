# apps/certification_bodies/views.py

"""
Views for the Certification Bodies app.

This module contains views for listing certification bodies and displaying their details.
"""

from django.shortcuts import get_object_or_404, render

from .models import CertBody


def certbody_list_view(request):
    """
    View for listing all certification bodies.
    """
    cert_bodies = CertBody.objects.all()
    return render(request, 'certification_bodies/certbody_list.html', {'cert_bodies': cert_bodies})

def certbody_detail_view(request, cb_id):
    """
    View for displaying the details of a specific certification body.
    """
    cert_body = get_object_or_404(CertBody, id=cb_id)
    return render(request, 'certification_bodies/certbody_detail.html', {'cert_body': cert_body})
