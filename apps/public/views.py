# apps/public/views.py

"""
Views for the Public app.

This module provides views for public users to search and verify certifications.
"""

from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.db.models import Q
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from apps.organizations.models import Certification
from .models import CertificationVerification, SearchLog
from .forms import CertificateSearchForm


def get_client_ip(request):
    """
    Get the client IP address from the request.
    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


class CertificateSearchView(ListView):
    """
    View for searching certifications.
    """

    model = Certification
    template_name = "public/certificate_search.html"
    context_object_name = "certifications"
    paginate_by = 10

    def get_queryset(self):
        queryset = Certification.objects.filter(
            organization__is_active=True, expiry_date__gte=timezone.now().date()
        )

        form = CertificateSearchForm(self.request.GET)
        if form.is_valid():
            search_term = form.cleaned_data.get("search_term")
            standard = form.cleaned_data.get("standard")

            # Log the search
            SearchLog.objects.create(
                search_term=search_term or "",
                ip_address=get_client_ip(self.request),
                results_count=0,  # Will update after filtering
            )

            if search_term:
                queryset = queryset.filter(
                    Q(organization__name__icontains=search_term)
                    | Q(certificate_number__icontains=search_term)
                    | Q(scope__icontains=search_term)
                )

            if standard:
                queryset = queryset.filter(standard=standard)

            # Update the search log with results count
            SearchLog.objects.filter(
                search_term=search_term or "", ip_address=get_client_ip(self.request)
            ).update(results_count=queryset.count())

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = CertificateSearchForm(self.request.GET)
        return context


class CertificateDetailView(DetailView):
    """
    View for displaying certificate details.
    """

    model = Certification
    template_name = "public/certificate_detail.html"
    context_object_name = "certificate"

    def get_object(self, queryset=None):
        certificate = super().get_object(queryset)

        # Log the verification
        CertificationVerification.objects.create(
            certificate=certificate,
            ip_address=get_client_ip(self.request),
            user_agent=self.request.META.get("HTTP_USER_AGENT", ""),
        )

        return certificate


@require_http_methods(["GET"])
def verify_certificate_api(request):
    """
    API endpoint for verifying a certificate by number.
    """
    certificate_number = request.GET.get("certificate_number")
    if not certificate_number:
        return JsonResponse({"error": "Certificate number is required"}, status=400)

    try:
        certificate = Certification.objects.get(certificate_number=certificate_number)

        # Log the verification
        CertificationVerification.objects.create(
            certificate=certificate,
            ip_address=get_client_ip(request),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )

        return JsonResponse(
            {
                "valid": certificate.is_valid,
                "organization": certificate.organization.name,
                "standard": certificate.standard,
                "issue_date": certificate.issue_date.isoformat(),
                "expiry_date": certificate.expiry_date.isoformat(),
                "cert_body": certificate.cert_body.name,
                "scope": certificate.scope,
            }
        )
    except Certification.DoesNotExist:
        return JsonResponse({"error": "Certificate not found"}, status=404)


def certificate_verification_view(request):
    """
    View for verifying certificates.
    """
    certificate_number = request.GET.get("certificate_number")
    context = {
        "page_title": "Certificate Verification",
        "description": "Verify certification status",
    }

    if certificate_number:
        certifications = Certification.objects.filter(
            certificate_number=certificate_number,
            organization__is_active=True,
            expiry_date__gte=timezone.now().date(),
        )

        if not certifications.exists():
            context["error_message"] = "No certificate found"
            return render(request, "public/certificate_search.html", context)

        context["certifications"] = certifications
    else:
        # Show all valid certifications by default
        context["certifications"] = Certification.objects.filter(
            organization__is_active=True, expiry_date__gte=timezone.now().date()
        )

    return render(request, "public/certificate_search.html", context)


def home_view(request):
    """
    Home page view.
    """
    return render(
        request,
        "public/home.html",
        {
            "page_title": "Welcome to ScopeWatch",
            "description": "Verify certifications of organizations",
        },
    )


def search_certified_organizations_view(request):
    """
    Search view for certified organizations.
    """
    query = request.GET.get("query")
    context = {
        "page_title": "Search Certified Organizations",
        "description": "Find organizations with valid certifications",
    }

    if query:
        certifications = Certification.objects.filter(
            Q(organization__name__icontains=query)
            | Q(certificate_number__icontains=query)
            | Q(scope__icontains=query),
            organization__is_active=True,
            expiry_date__gte=timezone.now().date(),
        )

        # Log the search
        SearchLog.objects.create(
            search_term=query,
            ip_address=get_client_ip(request),
            results_count=certifications.count(),
        )

        context["certifications"] = certifications
        context["query"] = query

        if not certifications.exists():
            context["no_results"] = True
    else:
        # Default view with all certifications
        context["certifications"] = Certification.objects.filter(
            organization__is_active=True, expiry_date__gte=timezone.now().date()
        )

    return render(request, "public/certificate_search.html", context)
