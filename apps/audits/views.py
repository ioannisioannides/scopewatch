# apps/audits/views.py

"""
Views for the Audits app.

This module contains views for listing audits and displaying audit details.
"""

from django.shortcuts import render, get_object_or_404
from .models import Audit

def audit_list_view(request):
    """
    View for listing all audits.

    Retrieves all audits from the database and renders them in the 'audit_list.html' template.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered HTML response containing the list of audits.
    """
    audits = Audit.objects.all()
    return render(request, 'audits/audit_list.html', {'audits': audits})

def audit_detail_view(request, audit_id):
    """
    View for displaying the details of a specific audit.

    Retrieves the audit with the given ID and renders it in the 'audit_detail.html' template.

    Args:
        request (HttpRequest): The HTTP request object.
        audit_id (int): The ID of the audit to retrieve.

    Returns:
        HttpResponse: The rendered HTML response containing the audit details.
    """
    audit = get_object_or_404(Audit, id=audit_id)
    return render(request, 'audits/audit_detail.html', {'audit': audit})
