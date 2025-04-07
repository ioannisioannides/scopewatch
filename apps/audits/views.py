# apps/audits/views.py

"""
Views for the Audits app.

This module contains views for listing audits and displaying audit details.
"""

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse

from .models import Audit


def audit_list(request):
    """
    View for listing all audits.

    Retrieves all audits from the database and renders them in the 'audit_list.html' template.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered HTML response containing the list of audits.
    """
    audits = Audit.objects.all()
    return render(request, "audits/audit_list.html", {"audits": audits})


def audit_detail(request, id):
    """
    View for displaying the details of a specific audit.

    Retrieves the audit with the given ID and renders it in the 'audit_detail.html' template.

    Args:
        request (HttpRequest): The HTTP request object.
        id (int): The ID of the audit to retrieve.

    Returns:
        HttpResponse: The rendered HTML response containing the audit details.
    """
    audit = get_object_or_404(Audit, id=id)
    return render(request, "audits/audit_detail.html", {"audit": audit})


def debug_view(request):
    """
    View for debugging the request path.

    Logs the request path and returns it in the response.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The response containing the request path.
    """
    return HttpResponse(f"Debugging: {request.path}")
