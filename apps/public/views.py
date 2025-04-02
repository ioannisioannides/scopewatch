# apps/public/views.py

from django.http import HttpResponse
from django.shortcuts import render

def public_home_view(request):
    """
    Example view for a public homepage or search form.
    """
    return HttpResponse("Welcome to the Public Portal")

def certificate_search_view(request):
    """
    Example placeholder for a certificate search page.
    """
    return HttpResponse("Certificate Search Placeholder")

def home_view(request):
    """
    View for the root URL (homepage).

    Returns:
        HttpResponse: Renders the homepage template.
    """
    return render(request, 'public/home.html')

def search_certified_organizations_view(request):
    """
    View for searching certified organizations.

    Returns:
        HttpResponse: Renders the search page template.
    """
    return render(request, 'public/search.html')
