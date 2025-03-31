# apps/certification_bodies/views.py

"""
Views for the Certification Bodies app.

This module contains views for listing certification bodies and displaying their details.
"""

from django.http import HttpResponse
from django.utils.html import escape

def certbody_list_view(request):
    """
    View for listing all certification bodies.

    Returns:
        HttpResponse: A placeholder response for the certification body list.
    """
    return HttpResponse("Cert Bodies Placeholder")

def certbody_detail_view(request, cb_id):
    """
    View for displaying the details of a specific certification body.

    Args:
        request (HttpRequest): The HTTP request object.
        cb_id (int): The ID of the certification body to retrieve.

    Returns:
        HttpResponse: A placeholder response for the certification body details.
    """
    return HttpResponse(f"Detail of Certification Body ID: {escape(cb_id)}")
