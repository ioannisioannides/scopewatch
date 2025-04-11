# apps/organizations/test_api.py

"""
Tests for the Organizations API.

This module contains tests for the Organizations app's API views and serializers.
"""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from apps.certification_bodies.models import CertBody
from apps.utils.test_credentials import get_test_credential

from .models import Certification, Organization
from .serializers import (
    CertificationSerializer,
    OrganizationDetailSerializer,
    OrganizationSerializer,
)

User = get_user_model()


class OrganizationAPITest(APITestCase):
    """Test suite for the Organization API endpoints."""

    def setUp(self):
        """Set up test data."""
        # Create a user for authentication
        self.user = User.objects.create_user(
            username=get_test_credential("api", "username"),
            password=get_test_credential("api", "password"),
        )
        self.client = APIClient()

        # Create test organizations
        self.organization1 = Organization.objects.create(
            name="Test Organization 1",
            industry="Technology",
            contact_email="org1@example.com",
            is_active=True,
        )
        self.organization2 = Organization.objects.create(
            name="Test Organization 2",
            industry="Healthcare",
            contact_email="org2@example.com",
            is_active=True,
        )

        # Create cert body for certifications
        self.cert_body = CertBody.objects.create(
            name="Test Cert Body",
            accreditation_id="TCB123",
            is_active=True,
        )

        # Create certifications
        self.certification = Certification.objects.create(
            organization=self.organization1,
            certificate_number="CERT-123",
            standard="ISO 9001",
            issue_date=timezone.now().date(),
            expiry_date=timezone.now().date() + timedelta(days=365 * 3),
            cert_body=self.cert_body,
            scope="Quality Management System",
        )

        # Define API URLs
        self.organizations_url = reverse("organizations-api:organization-list")
        self.organization_detail_url = reverse(
            "organizations-api:organization-detail", args=[self.organization1.pk]
        )
        self.certifications_url = reverse(
            "organizations-api:organization-certifications", args=[self.organization1.pk]
        )

    def test_get_organizations_unauthenticated(self):
        """Test that unauthenticated users cannot access organization list."""
        response = self.client.get(self.organizations_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_organizations_authenticated(self):
        """Test that authenticated users can access organization list."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.organizations_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Should return 2 organizations

        # Verify serialized data
        organizations = Organization.objects.all()
        serializer = OrganizationSerializer(organizations, many=True)
        self.assertEqual(response.data, serializer.data)

    def test_get_organization_detail(self):
        """Test retrieving a specific organization."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.organization_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify we get the detailed serializer
        organization = Organization.objects.get(pk=self.organization1.pk)
        serializer = OrganizationDetailSerializer(organization)
        self.assertEqual(response.data, serializer.data)

    def test_create_organization(self):
        """Test creating a new organization."""
        self.client.force_authenticate(user=self.user)
        new_organization_data = {
            "name": "New Test Organization",
            "industry": "Manufacturing",
            "contact_email": "new@example.com",
            "is_active": True,
        }

        response = self.client.post(self.organizations_url, new_organization_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify organization was created
        self.assertTrue(Organization.objects.filter(name="New Test Organization").exists())

        # Check the returned data
        self.assertEqual(response.data["name"], "New Test Organization")
        self.assertEqual(response.data["contact_email"], "new@example.com")

    def test_update_organization(self):
        """Test updating an existing organization."""
        self.client.force_authenticate(user=self.user)
        updated_data = {
            "name": "Updated Organization",
            "contact_email": "updated@example.com",
            "is_active": True,
        }

        response = self.client.put(self.organization_detail_url, updated_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify organization was updated
        self.organization1.refresh_from_db()
        self.assertEqual(self.organization1.name, "Updated Organization")
        self.assertEqual(self.organization1.contact_email, "updated@example.com")

    def test_delete_organization(self):
        """Test deleting an organization."""
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.organization_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verify organization was deleted
        self.assertFalse(Organization.objects.filter(pk=self.organization1.pk).exists())

    def test_get_certifications(self):
        """Test retrieving certifications for an organization."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.certifications_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify certification data
        certifications = self.organization1.certifications.all()
        serializer = CertificationSerializer(certifications, many=True)
        self.assertEqual(response.data, serializer.data)


class CertificationAPITest(APITestCase):
    """Test suite for the Certification API endpoints."""

    def setUp(self):
        """Set up test data."""
        # Create a user for authentication
        self.user = User.objects.create_user(
            username=get_test_credential("api_alt", "username"),
            password=get_test_credential("api_alt", "password"),
        )
        self.client = APIClient()

        # Create organization and cert body
        self.organization = Organization.objects.create(
            name="Certified Org",
            industry="Technology",
            contact_email="certorg@example.com",
            is_active=True,
        )
        self.cert_body = CertBody.objects.create(
            name="API Cert Body",
            accreditation_id="ACB456",
            is_active=True,
        )

        # Create certification
        self.certification = Certification.objects.create(
            organization=self.organization,
            certificate_number="API-CERT-123",
            standard="ISO 27001",
            issue_date=timezone.now().date(),
            expiry_date=timezone.now().date() + timedelta(days=365 * 3),
            cert_body=self.cert_body,
            scope="Information Security Management",
        )

        # Define API URLs
        self.certifications_list_url = reverse("organizations-api:certification-list")
        self.certification_detail_url = reverse(
            "organizations-api:certification-detail", args=[self.certification.pk]
        )

    def test_get_certifications_unauthenticated(self):
        """Test that unauthenticated users cannot access certification list."""
        response = self.client.get(self.certifications_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_certifications_authenticated(self):
        """Test that authenticated users can access certification list."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.certifications_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Should return 1 certification

        # Verify serialized data
        certifications = Certification.objects.all()
        serializer = CertificationSerializer(certifications, many=True)
        self.assertEqual(response.data, serializer.data)

    def test_get_certification_detail(self):
        """Test retrieving a specific certification."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.certification_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify serialized data
        certification = Certification.objects.get(pk=self.certification.pk)
        serializer = CertificationSerializer(certification)
        self.assertEqual(response.data, serializer.data)

    def test_create_certification(self):
        """Test creating a new certification."""
        self.client.force_authenticate(user=self.user)
        new_certification_data = {
            "organization": self.organization.pk,
            "certificate_number": "NEW-CERT-789",
            "standard": "ISO 14001",
            "issue_date": timezone.now().date().isoformat(),
            "expiry_date": (timezone.now().date() + timedelta(days=365 * 3)).isoformat(),
            "cert_body": self.cert_body.pk,
            "scope": "Environmental Management",
        }

        response = self.client.post(
            self.certifications_list_url, new_certification_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify certification was created
        self.assertTrue(Certification.objects.filter(certificate_number="NEW-CERT-789").exists())

    def test_update_certification(self):
        """Test updating an existing certification."""
        self.client.force_authenticate(user=self.user)
        updated_data = {
            "organization": self.organization.pk,
            "certificate_number": "UPDATED-CERT",
            "standard": "ISO 27001",
            "issue_date": timezone.now().date().isoformat(),
            "expiry_date": (timezone.now().date() + timedelta(days=365 * 3)).isoformat(),
            "cert_body": self.cert_body.pk,
            "scope": "Updated scope",
        }

        response = self.client.put(self.certification_detail_url, updated_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify certification was updated
        self.certification.refresh_from_db()
        self.assertEqual(self.certification.certificate_number, "UPDATED-CERT")
        self.assertEqual(self.certification.scope, "Updated scope")

    def test_delete_certification(self):
        """Test deleting a certification."""
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.certification_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verify certification was deleted
        self.assertFalse(Certification.objects.filter(pk=self.certification.pk).exists())


class SerializerTest(APITestCase):
    """Test suite for organization serializers."""

    def setUp(self):
        """Set up test data."""
        # Create test objects
        self.organization = Organization.objects.create(
            name="Serializer Test Org",
            industry="Finance",
            contact_email="serializer@example.com",
            is_active=True,
            address="123 Test Street",
            website="https://example.com",
        )
        self.cert_body = CertBody.objects.create(
            name="Serializer CB",
            accreditation_id="SCB789",
            is_active=True,
        )
        self.certification = Certification.objects.create(
            organization=self.organization,
            certificate_number="SERIAL-123",
            standard="ISO 9001",
            issue_date=timezone.now().date(),
            expiry_date=timezone.now().date() + timedelta(days=365 * 3),
            cert_body=self.cert_body,
            scope="Serializer Testing Scope",
        )

    def test_organization_serializer(self):
        """Test the organization serializer."""
        serializer = OrganizationSerializer(self.organization)
        data = serializer.data

        # Verify basic fields
        self.assertEqual(data["name"], "Serializer Test Org")
        self.assertEqual(data["contact_email"], "serializer@example.com")
        self.assertTrue(data["is_active"])

        # Verify related certifications
        self.assertEqual(len(data["certifications"]), 1)
        self.assertEqual(data["certifications"][0]["certificate_number"], "SERIAL-123")

    def test_organization_detail_serializer(self):
        """Test the organization detail serializer."""
        serializer = OrganizationDetailSerializer(self.organization)
        data = serializer.data

        # Verify fields
        self.assertEqual(data["name"], "Serializer Test Org")
        self.assertEqual(data["contact_email"], "serializer@example.com")

        # Verify related certifications
        self.assertEqual(len(data["certifications"]), 1)
        self.assertEqual(data["certifications"][0]["certificate_number"], "SERIAL-123")

    def test_certification_serializer(self):
        """Test the certification serializer."""
        serializer = CertificationSerializer(self.certification)
        data = serializer.data

        # Verify fields
        self.assertEqual(data["certificate_number"], "SERIAL-123")
        self.assertEqual(data["organization"], self.organization.id)
        self.assertEqual(data["cert_body"], self.cert_body.id)
        # Date fields are serialized to string
        self.assertTrue(isinstance(data["issue_date"], str))
        self.assertTrue(isinstance(data["expiry_date"], str))
