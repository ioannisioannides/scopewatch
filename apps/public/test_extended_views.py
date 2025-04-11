"""
Extended tests for the Public app's views.

This module contains additional tests for the Public app's views,
focusing on edge cases and previously uncovered code paths.
"""

from datetime import timedelta

from django.test import Client, RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone

from apps.certification_bodies.models import CertBody
from apps.organizations.models import Certification, Organization

from .forms import CertificateSearchForm
from .models import CertificationVerification, SearchLog
from .views import get_client_ip


class ExtendedPublicViewTest(TestCase):
    """
    Additional tests for the Public app's views focusing on edge cases.
    """

    def setUp(self):
        """
        Set up test data for extended view tests.
        """
        self.factory = RequestFactory()
        self.client = Client()

        # Create organizations
        self.active_org = Organization.objects.create(
            name="Active Organization", industry="Technology", is_active=True
        )
        self.inactive_org = Organization.objects.create(
            name="Inactive Organization", industry="Manufacturing", is_active=False
        )

        # Create cert body
        self.cert_body = CertBody.objects.create(
            name="Extended Test Certifier", accreditation_id="ETC-789"
        )

        today = timezone.now().date()

        # Create certifications with different properties
        self.active_cert = Certification.objects.create(
            organization=self.active_org,
            cert_body=self.cert_body,
            certificate_number="ACTIVE-9001",
            standard="ISO 9001:2015",
            issue_date=today - timedelta(days=365),
            expiry_date=today + timedelta(days=365),
            scope="Quality Management System",
        )

        self.expired_cert = Certification.objects.create(
            organization=self.active_org,
            cert_body=self.cert_body,
            certificate_number="EXPIRED-9001",
            standard="ISO 9001:2015",
            issue_date=today - timedelta(days=1000),
            expiry_date=today - timedelta(days=10),
            scope="Expired Quality Management System",
        )

        self.inactive_org_cert = Certification.objects.create(
            organization=self.inactive_org,
            cert_body=self.cert_body,
            certificate_number="INACTIVE-ORG-9001",
            standard="ISO 9001:2015",
            issue_date=today - timedelta(days=100),
            expiry_date=today + timedelta(days=600),
            scope="Quality Management System for inactive org",
        )

    def test_search_log_creation_with_blank_search(self):
        """
        Test SearchLog creation when search_term is blank.
        """
        # Clear any existing logs
        SearchLog.objects.all().delete()

        # Test with blank search term (form valid but term is empty)
        response = self.client.get(reverse("certificate_search") + "?search_term=")

        # Check if a log was created with empty search term
        self.assertEqual(SearchLog.objects.count(), 1)
        log = SearchLog.objects.first()
        self.assertEqual(log.search_term, "")

    def test_certificate_verification_view_edge_cases(self):
        """
        Test certificate_verification_view with various scenarios.
        """
        # Test with inactive organization's certificate
        response = self.client.get(
            reverse("certificate_verification") + "?certificate_number=INACTIVE-ORG-9001"
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, "No certificate found"
        )  # Should not find inactive org's certs

        # Test with expired certificate
        response = self.client.get(
            reverse("certificate_verification") + "?certificate_number=EXPIRED-9001"
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No certificate found")  # Should not find expired certs

    def test_search_certified_organizations_view_edge_cases(self):
        """
        Test search_certified_organizations_view with various scenarios.
        """
        # Test with no query parameter
        response = self.client.get(reverse("search_certified_organizations"))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("no_results", response.context)  # No query, so no "no results" message

        # Test with empty query
        response = self.client.get(reverse("search_certified_organizations") + "?query=")
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("no_results", response.context)  # Empty query should show all active certs

        # Test with query that returns no results
        response = self.client.get(
            reverse("search_certified_organizations") + "?query=NonExistentTerm"
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["no_results"])  # Should show no results message

        # Verify search log was created for no-results search
        log = SearchLog.objects.latest("search_date")
        self.assertEqual(log.search_term, "NonExistentTerm")
        self.assertEqual(log.results_count, 0)

    def test_verify_certificate_api_with_multi_ip_header(self):
        """
        Test verify_certificate_api with multiple IPs in X-Forwarded-For.
        """
        # Setup a request with multiple forwarded IPs
        self.client.defaults["HTTP_X_FORWARDED_FOR"] = "192.168.1.2, 10.0.0.1, 8.8.8.8"

        # Make request to the API
        response = self.client.get(
            reverse("verify_certificate_api")
            + f"?certificate_number={self.active_cert.certificate_number}"
        )
        self.assertEqual(response.status_code, 200)

        # Check that the verification was logged with the first IP
        verification = CertificationVerification.objects.latest("created_at")
        self.assertEqual(verification.ip_address, "192.168.1.2")

    def test_get_client_ip_with_ipv6(self):
        """
        Test get_client_ip function with IPv6 address.
        """
        # Create a mock request with IPv6
        request = self.factory.get("/")
        request.META["REMOTE_ADDR"] = "2001:0db8:85a3:0000:0000:8a2e:0370:7334"

        ip = get_client_ip(request)
        self.assertEqual(ip, "2001:0db8:85a3:0000:0000:8a2e:0370:7334")

    def test_certificate_search_form_validation(self):
        """
        Test CertificateSearchForm validation behavior.
        """
        # Test with valid data
        form = CertificateSearchForm(data={"search_term": "test", "standard": "ISO 9001:2015"})
        self.assertTrue(form.is_valid())

        # Test with empty data (should still be valid)
        form = CertificateSearchForm(data={})
        self.assertTrue(form.is_valid())

        # Test with standard only
        form = CertificateSearchForm(data={"standard": "ISO 14001:2015"})
        self.assertTrue(form.is_valid())

    def test_multiple_search_logs_with_same_term(self):
        """
        Test creating multiple search logs with the same term.
        """
        # Clear existing logs
        SearchLog.objects.all().delete()

        # Make multiple searches with the same term
        self.client.get(reverse("search_certified_organizations") + "?query=Active")
        self.client.get(reverse("search_certified_organizations") + "?query=Active")
        self.client.get(reverse("search_certified_organizations") + "?query=Active")

        # Should have created 3 log entries
        self.assertEqual(SearchLog.objects.filter(search_term="Active").count(), 3)

        # Each should have the same result count
        result_counts = SearchLog.objects.filter(search_term="Active").values_list(
            "results_count", flat=True
        )
        self.assertEqual(list(result_counts), [1, 1, 1])  # Each search found 1 certificate
