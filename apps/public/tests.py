# apps/public/tests.py

"""
Unit tests for the Public app.

This module contains test cases for the public-facing views and functionality.
"""

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from apps.organizations.models import Organization, Certification
from apps.certification_bodies.models import CertBody


class PublicAppTest(TestCase):
    """
    Test suite for general Public app functionality.
    """

    def setUp(self):
        """
        Set up test data for the Public app tests.
        """
        self.organization = Organization.objects.create(
            name="Public Test Org", contact_email="public@example.com"
        )
        self.cert_body = CertBody.objects.create(
            name="Public Certifier", accreditation_id="PCB123"
        )

        # Create certifications with different validity periods
        today = timezone.now().date()

        # Valid certification
        self.valid_certification = Certification.objects.create(
            organization=self.organization,
            cert_body=self.cert_body,
            certificate_number="VALID-12345",
            standard="ISO 9001:2015",
            issue_date=today - timedelta(days=30),
            expiry_date=today + timedelta(days=335),
        )

        # Expired certification
        self.expired_certification = Certification.objects.create(
            organization=self.organization,
            cert_body=self.cert_body,
            certificate_number="EXPIRED-67890",
            standard="ISO 14001:2015",
            issue_date=today - timedelta(days=400),
            expiry_date=today - timedelta(days=35),
        )

    def test_certification_validity(self):
        """
        Test the certification validity property.
        """
        self.assertTrue(self.valid_certification.is_valid)
        self.assertFalse(self.expired_certification.is_valid)


class PublicViewTest(TestCase):
    """
    Test suite for Public app views.
    """

    def setUp(self):
        """
        Set up test data for the Public app view tests.
        """
        self.organization = Organization.objects.create(
            name="ViewTest Organization", contact_email="viewtest@example.com"
        )
        self.cert_body = CertBody.objects.create(
            name="ViewTest Certifier", accreditation_id="VTC456"
        )

        today = timezone.now().date()
        self.certification = Certification.objects.create(
            organization=self.organization,
            cert_body=self.cert_body,
            certificate_number="VIEW-TEST-123",
            standard="ISO 27001:2022",
            issue_date=today - timedelta(days=60),
            expiry_date=today + timedelta(days=305),
        )

    def test_home_view(self):
        """
        Test the home view.

        This test ensures that the home view returns a 200 status code
        and contains the expected content.
        """
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Scopewatch")

    def test_search_view(self):
        """
        Test the search view.
        """
        response = self.client.get(reverse("search_certified_organizations"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Search")

        # Test search functionality
        response = self.client.get(
            reverse("search_certified_organizations") + "?query=ViewTest"
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ViewTest Organization")

        # Test with no results
        response = self.client.get(
            reverse("search_certified_organizations") + "?query=NonExistentOrg"
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "ViewTest Organization")

    def test_certificate_verification_view(self):
        """
        Test the certificate verification view.
        """
        # Test without certificate number
        response = self.client.get(reverse("certificate_verification"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Certificate Verification")

        # Test with valid certificate number
        response = self.client.get(
            reverse("certificate_verification") + "?certificate_number=VIEW-TEST-123"
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ViewTest Organization")
        self.assertContains(response, "ISO 27001:2022")

        # Test with invalid certificate number
        response = self.client.get(
            reverse("certificate_verification") + "?certificate_number=INVALID-NUMBER"
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No certificate found")
