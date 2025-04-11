"""
Comprehensive tests for the Public app's views.

This module focuses on improving coverage for all views in the public app,
particularly targeting untested code paths.
"""

import json
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone

User = get_user_model()

from apps.certification_bodies.models import CertBody
from apps.organizations.models import Certification, Organization
from apps.utils.test_credentials import get_test_credential

from .models import CertificationVerification, SearchLog
from .views import (
    CertificateDetailView,
    CertificateSearchView,
    certificate_verification_view,
    get_client_ip,
    home_view,
    search_certified_organizations_view,
    verify_certificate_api,
)


class PublicViewsCoverageTest(TestCase):
    """Test suite specifically designed to improve coverage of public app views."""

    def setUp(self):
        """Set up test data."""
        self.factory = RequestFactory()

        # Create organizations - active and inactive
        self.active_org = Organization.objects.create(
            name="Coverage Test Org",
            industry="Manufacturing",
            contact_email="coverage@example.com",
            website="https://coveragetest.com",
            is_active=True,
        )

        self.inactive_org = Organization.objects.create(
            name="Inactive Test Org",
            industry="Transportation",
            contact_email="inactive@example.com",
            is_active=False,
        )

        # Create certification body
        self.cert_body = CertBody.objects.create(
            name="Coverage CB",
            accreditation_id="COVCB-123",
            is_active=True,
        )

        # Create dates
        today = timezone.now().date()

        # Create certifications - valid and expired
        self.valid_certification = Certification.objects.create(
            organization=self.active_org,
            certificate_number="COV-VALID-123",
            standard="ISO 9001:2015",
            issue_date=today - timedelta(days=30),
            expiry_date=today + timedelta(days=335),
            cert_body=self.cert_body,
            scope="Quality Management System for testing",
        )

        self.expired_certification = Certification.objects.create(
            organization=self.active_org,
            certificate_number="COV-EXPIRED-456",
            standard="ISO 14001:2015",
            issue_date=today - timedelta(days=500),
            expiry_date=today - timedelta(days=135),
            cert_body=self.cert_body,
            scope="Expired Environmental Management System",
        )

        self.inactive_org_certification = Certification.objects.create(
            organization=self.inactive_org,
            certificate_number="COV-INACTIVE-789",
            standard="ISO 27001:2022",
            issue_date=today - timedelta(days=30),
            expiry_date=today + timedelta(days=335),
            cert_body=self.cert_body,
            scope="Information Security for inactive org",
        )

        # Create a user for testing
        self.user = User.objects.create_user(
            username=get_test_credential("default", "username", "coverage_tester"),
            email=get_test_credential("default", "email", "coverage@example.com"),
            password=get_test_credential("default", "password", "coverage_pass"),
        )

        # Clear any search logs
        SearchLog.objects.all().delete()
        CertificationVerification.objects.all().delete()

    def test_certificate_search_view_with_invalid_form(self):
        """Test CertificateSearchView with an invalid form."""
        # Create a request with invalid parameters to test form validation
        url = reverse("certificate_search") + "?standard=INVALID-STANDARD"
        response = self.client.get(url)

        # Should still return 200 even with invalid form
        self.assertEqual(response.status_code, 200)

        # Should return all valid certificates as a fallback
        self.assertEqual(len(response.context["certifications"]), 1)
        self.assertEqual(response.context["certifications"][0], self.valid_certification)

    def test_certificate_search_view_form_validation_branch(self):
        """Test the form validation branch in CertificateSearchView."""
        # Setup a request with both search_term and standard
        url = reverse("certificate_search") + "?search_term=Coverage&standard=ISO+9001:2015"
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["certifications"]), 1)

        # Verify that a search log was created with the correct results count
        search_log = SearchLog.objects.latest("created_at")
        self.assertEqual(search_log.search_term, "Coverage")
        self.assertEqual(search_log.results_count, 1)

    def test_certificate_search_with_no_search_parameters(self):
        """Test certificate search view with no search parameters."""
        # Should show all valid certificates
        url = reverse("certificate_search")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["certifications"]), 1)
        self.assertIn(self.valid_certification, response.context["certifications"])
        self.assertNotIn(self.expired_certification, response.context["certifications"])

    def test_search_logs_updated_with_results_count(self):
        """Test that search logs are updated with the correct results count."""
        # First search creates log
        self.client.get(reverse("certificate_search") + "?search_term=initial")

        # Verify initial log
        initial_log = SearchLog.objects.latest("created_at")
        self.assertEqual(initial_log.search_term, "initial")
        self.assertEqual(initial_log.results_count, 0)  # No results for "initial"

        # Second search with same term and IP would update results count if implementation changed
        self.client.get(reverse("certificate_search") + "?search_term=initial")

        # There should be two logs with the same search term
        logs = SearchLog.objects.filter(search_term="initial")
        self.assertEqual(logs.count(), 2)

    def test_certificate_detail_view_records_verification(self):
        """Test that CertificateDetailView records a verification."""
        # Access the certificate detail
        url = reverse("certificate_detail", args=[self.valid_certification.pk])
        response = self.client.get(url)

        # Check if a verification was recorded
        self.assertEqual(response.status_code, 200)
        verifications = CertificationVerification.objects.filter(
            certificate=self.valid_certification
        )
        self.assertEqual(verifications.count(), 1)

        # Accessing again should record another verification
        response = self.client.get(url)
        verifications = CertificationVerification.objects.filter(
            certificate=self.valid_certification
        )
        self.assertEqual(verifications.count(), 2)

    def test_verify_certificate_api_with_edge_cases(self):
        """Test the verify_certificate_api with various edge cases."""
        # Test with no certificate number
        response = self.client.get(reverse("verify_certificate_api"))
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content["error"], "Certificate number is required")

        # Test with non-existent certificate
        response = self.client.get(
            reverse("verify_certificate_api") + "?certificate_number=NONEXISTENT"
        )
        self.assertEqual(response.status_code, 404)
        content = json.loads(response.content)
        self.assertEqual(content["error"], "Certificate not found")

        # Test with expired certificate
        response = self.client.get(
            reverse("verify_certificate_api")
            + f"?certificate_number={self.expired_certification.certificate_number}"
        )
        self.assertEqual(response.status_code, 404)

        # Test with inactive organization
        response = self.client.get(
            reverse("verify_certificate_api")
            + f"?certificate_number={self.inactive_org_certification.certificate_number}"
        )
        self.assertEqual(response.status_code, 404)

        # Test valid certificate
        response = self.client.get(
            reverse("verify_certificate_api")
            + f"?certificate_number={self.valid_certification.certificate_number}"
        )
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertTrue(content["valid"])
        self.assertEqual(content["organization"], "Coverage Test Org")

    def test_certificate_verification_view_multiple_certifications(self):
        """Test certificate_verification_view with multiple matching certifications."""
        # Create a second valid certification with the same number
        second_cert = Certification.objects.create(
            organization=self.active_org,
            certificate_number=self.valid_certification.certificate_number,  # Same number
            standard="ISO 45001:2018",
            issue_date=timezone.now().date() - timedelta(days=30),
            expiry_date=timezone.now().date() + timedelta(days=335),
            cert_body=self.cert_body,
            scope="Duplicate certificate number",
        )

        # Try to verify this certificate number
        url = (
            reverse("certificate_verification")
            + f"?certificate_number={self.valid_certification.certificate_number}"
        )
        response = self.client.get(url)

        # Should show both certificates
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["certifications"]), 2)
        self.assertIn(self.valid_certification, response.context["certifications"])
        self.assertIn(second_cert, response.context["certifications"])

    def test_search_certified_organizations_view_branches(self):
        """Test search_certified_organizations_view branches."""
        # Test with no query parameter (default view)
        response = self.client.get(reverse("search_certified_organizations"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["certifications"]), 1)
        self.assertNotIn("no_results", response.context)

        # Test with empty query parameter
        response = self.client.get(reverse("search_certified_organizations") + "?query=")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["certifications"]), 1)
        self.assertNotIn("no_results", response.context)

        # Test with query that matches
        response = self.client.get(reverse("search_certified_organizations") + "?query=Coverage")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["certifications"]), 1)
        self.assertEqual(response.context["query"], "Coverage")
        self.assertNotIn("no_results", response.context)

        # Test with query that doesn't match
        response = self.client.get(reverse("search_certified_organizations") + "?query=NoMatch")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["certifications"]), 0)
        self.assertEqual(response.context["query"], "NoMatch")
        self.assertTrue(response.context["no_results"])

        # Verify search log was created
        search_log = SearchLog.objects.latest("created_at")
        self.assertEqual(search_log.search_term, "NoMatch")
        self.assertEqual(search_log.results_count, 0)
