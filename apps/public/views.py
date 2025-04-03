# apps/public/views.py

from django.http import HttpResponse
from django.shortcuts import render

from apps.organizations.models import Certification, Organization


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
    return render(request, "public/home.html")


def search_certified_organizations_view(request):
    """
    View for searching certified organizations.

    Returns:
        HttpResponse: Renders the search page template with search results.
    """
    query = request.GET.get("query", "")
    cert_body = request.GET.get("cert_body", "")

    results = Certification.objects.filter(
        organization__name__icontains=query,
        cert_body__name__icontains=cert_body,
        is_active=True,
    )

    return render(
        request,
        "public/search.html",
        {"results": results, "query": query, "cert_body": cert_body},
    )


def certificate_verification_view(request):
    """
    View for verifying a certificate by its number.

    Returns:
        HttpResponse: Renders the certificate verification page with the result.
    """
    certificate_number = request.GET.get("certificate_number", "")
    certificate = Certification.objects.filter(
        certificate_number=certificate_number
    ).first()

    return render(
        request,
        "public/verify.html",
        {"certificate": certificate, "certificate_number": certificate_number},
    )
