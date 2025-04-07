# apps/consultants/views.py

"""
Views for the Consultants app.

This module contains placeholder views for listing consultants and consultancy firms.
These views can be expanded to include logic for rendering templates or returning JSON responses.
"""

from django.shortcuts import render

from .models import ConsultancyFirm, Consultant


def consultant_list_view(request):
    """
    View for listing all consultants.
    """
    consultants = Consultant.objects.all()
    return render(
        request, "consultants/consultant_list.html", {"consultants": consultants}
    )


def consultancy_firm_list_view(request):
    """
    View for listing all consultancy firms.
    """
    firms = ConsultancyFirm.objects.all()
    return render(request, "consultants/consultancy_firm_list.html", {"firms": firms})
