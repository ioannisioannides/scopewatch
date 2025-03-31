# apps/consultants/views.py

"""
Views for the Consultants app.

This module contains placeholder views for listing consultants and consultancy firms.
These views can be expanded to include logic for rendering templates or returning JSON responses.
"""

from django.http import HttpResponse

def consultant_list_view(request):
    """
    View for listing all consultants.

    Returns:
        HttpResponse: A placeholder response for the consultant list.
    """
    return HttpResponse("Consultant List Placeholder")

def consultancy_firm_list_view(request):
    """
    View for listing all consultancy firms.

    Returns:
        HttpResponse: A placeholder response for the consultancy firm list.
    """
    return HttpResponse("Consultancy Firm List Placeholder")
