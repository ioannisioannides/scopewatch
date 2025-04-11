# apps/public/tests.py

"""
Tests for the public app of the ScopeWatch project.

This module contains tests for views, models, and forms in the public app,
focusing on certificate search and verification functionality.
"""

import json  # Add missing import for json
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

User = get_user_model()

from apps.certification_bodies.models import CertBody
from apps.organizations.models import Certification, Organization
from apps.public.forms import CertificationVerificationForm
from apps.public.models import CertificationVerification
from apps.utils.test_credentials import get_test_credential

from .models import CertificationVerification, SearchLog


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
        self.cert_body = CertBody.objects.create(name="Public Certifier", accreditation_id="PCB123")

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
            scope="Information Security Management System for cloud services",
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
        response = self.client.get(reverse("search_certified_organizations") + "?query=ViewTest")
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

    def test_verify_certificate_api(self):
        """
        Test the certificate verification API endpoint.
        """
        # Test without certificate number
        response = self.client.get(reverse("public:verify_api"))
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content["error"], "Certificate number is required")

        # Test with valid certificate number
        response = self.client.get(
            reverse("public:verify_api")
            + f"?certificate_number={self.certification.certificate_number}"
        )
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertTrue(content["valid"])
        self.assertEqual(content["organization"], "ViewTest Organization")
        self.assertEqual(content["standard"], "ISO 27001:2022")
        self.assertEqual(content["cert_body"], "ViewTest Certifier")
        self.assertEqual(
            content["scope"],
            "Information Security Management System for cloud services",
        )

        # Verify that a verification log was created
        self.assertEqual(CertificationVerification.objects.count(), 1)
        verification = CertificationVerification.objects.first()
        self.assertEqual(verification.certificate, self.certification)

        # Test with invalid certificate number
        response = self.client.get(
            reverse("public:verify_api") + "?certificate_number=NONEXISTENT-CERT"
        )
        self.assertEqual(response.status_code, 404)
        content = json.loads(response.content)
        self.assertEqual(content["error"], "Certificate not found")

    def test_certificate_detail_view(self):
        """
        Test the certificate detail view.
        """
        response = self.client.get(
            reverse("public:certificate_detail", args=[self.certification.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ViewTest Organization")
        self.assertContains(response, "ISO 27001:2022")
        self.assertContains(response, "ViewTest Certifier")

        # Verify that a verification log was created
        self.assertEqual(CertificationVerification.objects.count(), 1)
        verification = CertificationVerification.objects.first()
        self.assertEqual(verification.certificate, self.certification)

    def test_get_client_ip(self):
        """
        Test the get_client_ip function.
        """
        from django.test.client import RequestFactory

        from .views import get_client_ip

        # Create a request factory
        factory = RequestFactory()

        # Test with X-Forwarded-For header
        request = factory.get("/")
        request.META["HTTP_X_FORWARDED_FOR"] = "192.168.1.1, 10.0.0.1"
        ip = get_client_ip(request)
        self.assertEqual(ip, "192.168.1.1")

        # Test without X-Forwarded-For header
        request = factory.get("/")
        request.META["REMOTE_ADDR"] = "192.168.1.2"
        ip = get_client_ip(request)
        self.assertEqual(ip, "192.168.1.2")


class CertificateSearchViewTest(TestCase):
    """
    Test suite specifically for the CertificateSearchView.
    """

    def setUp(self):
        """
        Set up test data for the CertificateSearchView tests.
        """
        # Create organizations
        self.org1 = Organization.objects.create(
            name="QualityFirst Manufacturing", industry="Manufacturing", is_active=True
        )
        self.org2 = Organization.objects.create(
            name="SecureIT Solutions", industry="IT Services", is_active=True
        )
        self.inactive_org = Organization.objects.create(
            name="Inactive Company", industry="Other", is_active=False
        )

        # Create cert body
        self.cert_body = CertBody.objects.create(
            name="Global Standards Authority", accreditation_id="GSA-CB"
        )

        today = timezone.now().date()

        # Create certifications
        self.cert1 = Certification.objects.create(
            organization=self.org1,
            cert_body=self.cert_body,
            certificate_number="QF-9001-2023",
            standard="ISO 9001:2015",
            issue_date=today - timedelta(days=180),
            expiry_date=today + timedelta(days=550),
            scope="Quality Management System for manufacturing operations",
        )

        self.cert2 = Certification.objects.create(
            organization=self.org2,
            cert_body=self.cert_body,
            certificate_number="SI-27001-2023",
            standard="ISO 27001:2022",
            issue_date=today - timedelta(days=90),
            expiry_date=today + timedelta(days=640),
            scope="Information Security Management System for cloud services",
        )

        self.expired_cert = Certification.objects.create(
            organization=self.org1,
            cert_body=self.cert_body,
            certificate_number="QF-14001-OLD",
            standard="ISO 14001:2015",
            issue_date=today - timedelta(days=1100),
            expiry_date=today - timedelta(days=10),
            scope="Environmental Management System",
        )

        self.inactive_org_cert = Certification.objects.create(
            organization=self.inactive_org,
            cert_body=self.cert_body,
            certificate_number="INACTIVE-45001",
            standard="ISO 45001:2018",
            issue_date=today - timedelta(days=200),
            expiry_date=today + timedelta(days=500),
            scope="Occupational Health and Safety Management System",
        )

    def test_certificate_search_view_basic(self):
        """
        Test basic functionality of the CertificateSearchView.
        """
        response = self.client.get(reverse("public:certificate_search"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "QualityFirst Manufacturing")
        self.assertContains(response, "SecureIT Solutions")

        # Should not contain expired certifications or inactive organizations
        self.assertNotContains(response, "QF-14001-OLD")
        self.assertNotContains(response, "Inactive Company")

        self.assertEqual(len(response.context["certifications"]), 2)

    def test_certificate_search_view_with_search_term(self):
        """
        Test searching by term in the CertificateSearchView.
        """
        # Search by organization name
        response = self.client.get(reverse("public:certificate_search") + "?search_term=Quality")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "QualityFirst Manufacturing")
        self.assertNotContains(response, "SecureIT Solutions")
        self.assertEqual(len(response.context["certifications"]), 1)

        # Search by certificate number
        response = self.client.get(reverse("public:certificate_search") + "?search_term=SI-27001")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "SecureIT Solutions")
        self.assertNotContains(response, "QualityFirst Manufacturing")

        # Search by scope
        response = self.client.get(reverse("public:certificate_search") + "?search_term=cloud")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "SecureIT Solutions")
        self.assertNotContains(response, "QualityFirst Manufacturing")

        # Verify search log was created
        self.assertEqual(SearchLog.objects.count(), 3)
        log = SearchLog.objects.latest("search_date")
        self.assertEqual(log.search_term, "cloud")
        self.assertEqual(log.results_count, 1)

    def test_certificate_search_view_with_standard(self):
        """
        Test filtering by standard in the CertificateSearchView.
        """
        response = self.client.get(reverse("public:certificate_search") + "?standard=ISO 9001:2015")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "QualityFirst Manufacturing")
        self.assertNotContains(response, "SecureIT Solutions")

        response = self.client.get(
            reverse("public:certificate_search") + "?standard=ISO 27001:2022"
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "SecureIT Solutions")
        self.assertNotContains(response, "QualityFirst Manufacturing")

    def test_certificate_search_view_with_combined_filters(self):
        """
        Test combining search term and standard filters.
        """
        response = self.client.get(
            reverse("public:certificate_search") + "?search_term=Quality&standard=ISO 9001:2015"
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "QualityFirst Manufacturing")
        self.assertEqual(len(response.context["certifications"]), 1)

        # No results case
        response = self.client.get(
            reverse("public:certificate_search") + "?search_term=NonExistent&standard=ISO 9001:2015"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["certifications"]), 0)

        # Verify search log was updated
        log = SearchLog.objects.latest("search_date")
        self.assertEqual(log.search_term, "NonExistent")
        self.assertEqual(log.results_count, 0)
