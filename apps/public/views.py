# apps/public/views.py

"""
Views for the Public app.

This module contains views for the public-facing pages of the Scopewatch project.
"""

from django.shortcuts import render
from django.http import HttpResponse

from apps.organizations.models import Certification, Organization


def public_home_view(request):
    """
    Example view for a public homepage or search form.
    """
    _ = request  # Explicitly mark 'request' as used
    return HttpResponse("Welcome to the Public Portal")


def certificate_search_view(request):
    """
    View for certificate search page.

    Args:
        request (HttpRequest): The HTTP request.

    Returns:
        HttpResponse: Rendered certificate search page.
    """
    return HttpResponse("Certificate Search Placeholder")


def home_view(request):
    """
    View for the root URL (homepage).

    Args:
        request (HttpRequest): The HTTP request.

    Returns:
        HttpResponse: Rendered homepage.
    """
    return render(request, "public/home.html")


def search_certified_organizations_view(request):
    """
    View for searching certified organizations.

    Args:
        request (HttpRequest): The HTTP request.

    Returns:
        HttpResponse: Rendered search page with results if query parameters are present.
    """
    query = request.GET.get('query', '')
    cert_body = request.GET.get('cert_body', '')
    
    results = []
    if query or cert_body:
        # Filter certifications based on query parameters
        certifications = Certification.objects.all()
        
        if query:
            certifications = certifications.filter(organization__name__icontains=query)
        
        if cert_body:
            certifications = certifications.filter(cert_body__name__icontains=cert_body)
        
        results = certifications
    
    return render(request, "public/search.html", {
        'query': query,
        'cert_body': cert_body,
        'results': results
    })


def certificate_verification_view(request):
    """
    View for verifying a certificate.

    Args:
        request (HttpRequest): The HTTP request.

    Returns:
        HttpResponse: Rendered certificate verification page with results if certificate number is provided.
    """
    certificate_number = request.GET.get('certificate_number', '')
    certificate = None
    
    if certificate_number:
        try:
            certificate = Certification.objects.get(certificate_number=certificate_number)
        except Certification.DoesNotExist:
            pass
    
    return render(request, "public/verify.html", {
        'certificate_number': certificate_number,
        'certificate': certificate
    })
