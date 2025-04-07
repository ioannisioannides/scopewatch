# apps/organizations/tests.py

"""
Unit tests for the Organizations app.

This module contains test cases for the Organization model and its functionality.
Expand these tests to cover additional scenarios and edge cases.
"""

from django.test import TestCase
from django.urls import reverse

from .models import Organization, Certification
from apps.certification_bodies.models import CertBody
from django.utils import timezone
from datetime import timedelta


class OrganizationModelTest(TestCase):
    """
    Test suite for the Organization model.

    This class contains unit tests for creating and validating
    Organization model instances.
    """

    def test_create_organization(self):
        """
        Test the creation of an Organization instance.

        This test ensures that an Organization instance can be created
        with valid data and that its attributes are correctly set.
        """
        org = Organization.objects.create(
            name="TestOrg", contact_email="contact@testorg.com"
        )
        self.assertEqual(org.name, "TestOrg")
        self.assertEqual(org.contact_email, "contact@testorg.com")
        self.assertTrue(org.is_active)

    def test_organization_creation(self):
        """
        Test the creation of an Organization instance with all attributes.
        """
        org = Organization.objects.create(
            name="Complete Test Org",
            contact_email="complete@testorg.com",
            address="123 Test Street, Test City",
            is_active=True
        )
        self.assertEqual(org.name, "Complete Test Org")
        self.assertEqual(org.address, "123 Test Street, Test City")
        self.assertTrue(org.is_active)
        self.assertIsNotNone(org.created_at)

    def test_organization_update(self):
        """
        Test updating an Organization instance.
        """
        org = Organization.objects.create(
            name="Original Name", 
            contact_email="original@example.com",
            is_active=True
        )
        
        # Update the organization
        org.name = "Updated Name"
        org.contact_email = "updated@example.com"
        org.is_active = False
        org.save()
        
        # Fetch the organization again from the database
        updated_org = Organization.objects.get(pk=org.pk)
        self.assertEqual(updated_org.name, "Updated Name")
        self.assertEqual(updated_org.contact_email, "updated@example.com")
        self.assertFalse(updated_org.is_active)


class OrganizationViewTest(TestCase):
    """
    Test suite for the Organization views.
    """

    def setUp(self):
        self.organization = Organization.objects.create(name="Test Org")

    def test_organization_list_view(self):
        """
        Test the organization list view.

        This test ensures that the organization list view returns a 200 status code
        and contains the expected organization data.
        """
        response = self.client.get(reverse("organization_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Org")

    def test_organization_detail_view(self):
        """
        Test the organization detail view.

        This test ensures that the organization detail view returns a 200 status code
        and contains the expected organization data.
        """
        response = self.client.get(
            reverse("organization_detail", args=[self.organization.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Org")


class CertificationModelTest(TestCase):
    """
    Test suite for the Certification model.
    """
    
    def setUp(self):
        self.organization = Organization.objects.create(
            name="Certified Org", 
            contact_email="certified@example.com"
        )
        self.cert_body = CertBody.objects.create(
            name="Certifier Inc",
            accreditation_id="CERT-123"
        )
    
    def test_certification_creation(self):
        """
        Test creating a certification.
        """
        today = timezone.now().date()
        expiry = today + timedelta(days=365)
        
        certification = Certification.objects.create(
            organization=self.organization,
            cert_body=self.cert_body,
            standard="ISO 9001:2015",
            certificate_number="ISO9001-123456",
            issue_date=today,
            expiry_date=expiry
        )
        
        self.assertEqual(certification.organization, self.organization)
        self.assertEqual(certification.cert_body, self.cert_body)
        self.assertEqual(certification.standard, "ISO 9001:2015")
        self.assertEqual(certification.certificate_number, "ISO9001-123456")
        
    def test_certification_validity(self):
        """
        Test certification validity property.
        """
        today = timezone.now().date()
        
        valid_cert = Certification.objects.create(
            organization=self.organization,
            cert_body=self.cert_body,
            standard="ISO 9001:2015",
            certificate_number="VALID-CERT",
            issue_date=today - timedelta(days=30),
            expiry_date=today + timedelta(days=335)
        )
        
        expired_cert = Certification.objects.create(
            organization=self.organization,
            cert_body=self.cert_body,
            standard="ISO 9001:2015",
            certificate_number="EXPIRED-CERT",
            issue_date=today - timedelta(days=400),
            expiry_date=today - timedelta(days=35)
        )
        
        self.assertTrue(valid_cert.is_valid)
        self.assertFalse(expired_cert.is_valid)
