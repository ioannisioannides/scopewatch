# apps/organizations/test_api.py

"""
API tests for the Organizations app.

This module contains test cases for the API views and serializers in the Organizations app.
"""

from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from apps.certification_bodies.models import CertBody
from .models import Organization, Certification
from .serializers import OrganizationSerializer, OrganizationDetailSerializer, CertificationSerializer


class OrganizationAPITestCase(APITestCase):
    """Test case for the Organization API."""

    def setUp(self):
        """Set up test data."""
        # Create a user for authentication
        self.user = User.objects.create_user(
            username="api_tester",
            email="api@example.com",
            password="secure_password"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        # Create test organizations
        self.org1 = Organization.objects.create(
            name="Test Organization 1",
            industry="Manufacturing",
            contact_email="contact@testorg1.com",
            is_active=True
        )
        self.org2 = Organization.objects.create(
            name="Test Organization 2",
            industry="Services",
            contact_email="contact@testorg2.com",
            is_active=True
        )

        # Create a certification body
        self.cert_body = CertBody.objects.create(
            name="API Test Cert Body",
            accreditation_id="API-CB"
        )

        # Create certifications
        self.cert1 = Certification.objects.create(
            organization=self.org1,
            cert_body=self.cert_body,
            certificate_number="API-CERT-001",
            standard="ISO 9001:2015"
        )

        # Define API endpoints
        self.org_list_url = reverse('api:organization-list')
        self.org1_detail_url = reverse('api:organization-detail', args=[self.org1.pk])
        self.org1_certs_url = reverse('api:organization-certifications', args=[self.org1.pk])
        self.cert_list_url = reverse('api:certification-list')
        self.cert1_detail_url = reverse('api:certification-detail', args=[self.cert1.pk])

    def test_organization_serializer(self):
        """Test that the OrganizationSerializer works correctly."""
        serializer = OrganizationSerializer(self.org1)
        expected_fields = ["id", "name", "contact_email", "is_active", "certifications"]
        for field in expected_fields:
            self.assertIn(field, serializer.data)
        self.assertEqual(serializer.data["name"], "Test Organization 1")
        self.assertEqual(serializer.data["contact_email"], "contact@testorg1.com")

    def test_organization_detail_serializer(self):
        """Test that the OrganizationDetailSerializer works correctly."""
        serializer = OrganizationDetailSerializer(self.org1)
        # Detail serializer should include certification data
        self.assertIn("certifications", serializer.data)
        self.assertEqual(len(serializer.data["certifications"]), 1)
        self.assertEqual(serializer.data["certifications"][0]["certificate_number"], "API-CERT-001")

    def test_certification_serializer(self):
        """Test that the CertificationSerializer works correctly."""
        serializer = CertificationSerializer(self.cert1)
        expected_fields = ["id", "certificate_number", "issue_date", "expiry_date", "organization", "cert_body"]
        for field in expected_fields:
            self.assertIn(field, serializer.data)
        self.assertEqual(serializer.data["certificate_number"], "API-CERT-001")
        self.assertEqual(serializer.data["organization"], self.org1.pk)
        self.assertEqual(serializer.data["cert_body"], self.cert_body.pk)

    def test_get_organization_list(self):
        """Test getting a list of organizations."""
        response = self.client.get(self.org_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["name"], "Test Organization 1")
        self.assertEqual(response.data[1]["name"], "Test Organization 2")

    def test_get_organization_detail(self):
        """Test getting organization detail."""
        response = self.client.get(self.org1_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Test Organization 1")
        # Detail view should use OrganizationDetailSerializer which includes certifications
        self.assertIn("certifications", response.data)

    def test_create_organization(self):
        """Test creating a new organization."""
        data = {
            "name": "New Test Organization",
            "contact_email": "new@testorg.com",
            "is_active": True
        }
        response = self.client.post(self.org_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Organization.objects.count(), 3)
        new_org = Organization.objects.get(name="New Test Organization")
        self.assertEqual(new_org.contact_email, "new@testorg.com")

    def test_update_organization(self):
        """Test updating an organization."""
        data = {
            "name": "Updated Organization",
            "contact_email": "updated@testorg.com",
            "is_active": True
        }
        response = self.client.put(self.org1_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.org1.refresh_from_db()
        self.assertEqual(self.org1.name, "Updated Organization")
        self.assertEqual(self.org1.contact_email, "updated@testorg.com")

    def test_partial_update_organization(self):
        """Test partially updating an organization."""
        data = {"name": "Partially Updated Org"}
        response = self.client.patch(self.org1_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.org1.refresh_from_db()
        self.assertEqual(self.org1.name, "Partially Updated Org")
        # Email should not have changed
        self.assertEqual(self.org1.contact_email, "contact@testorg1.com")

    def test_delete_organization(self):
        """Test deleting an organization."""
        response = self.client.delete(self.org1_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Organization.objects.count(), 1)
        # org1 should no longer exist
        with self.assertRaises(Organization.DoesNotExist):
            Organization.objects.get(pk=self.org1.pk)

    def test_get_organization_certifications(self):
        """Test getting certifications for a specific organization."""
        response = self.client.get(self.org1_certs_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["certificate_number"], "API-CERT-001")

    def test_authentication_required(self):
        """Test that authentication is required for API access."""
        # Create a client without authentication
        client = APIClient()
        response = client.get(self.org_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CertificationAPITestCase(APITestCase):
    """Test case for the Certification API."""

    def setUp(self):
        """Set up test data."""
        # Create a user for authentication
        self.user = User.objects.create_user(
            username="cert_api_tester",
            email="cert_api@example.com",
            password="secure_password"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        # Create organization and cert body
        self.org = Organization.objects.create(
            name="Cert Test Organization",
            industry="Manufacturing",
            is_active=True
        )
        self.cert_body = CertBody.objects.create(
            name="Cert API Test Body",
            accreditation_id="CERT-API-CB"
        )

        # Create a certification
        self.cert = Certification.objects.create(
            organization=self.org,
            cert_body=self.cert_body,
            certificate_number="CERT-API-001",
            standard="ISO 9001:2015",
            scope="Quality Management System"
        )

        # Define API endpoints
        self.cert_list_url = reverse('api:certification-list')
        self.cert_detail_url = reverse('api:certification-detail', args=[self.cert.pk])

    def test_get_certification_list(self):
        """Test getting a list of certifications."""
        response = self.client.get(self.cert_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["certificate_number"], "CERT-API-001")

    def test_get_certification_detail(self):
        """Test getting certification detail."""
        response = self.client.get(self.cert_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["certificate_number"], "CERT-API-001")
        self.assertEqual(response.data["standard"], "ISO 9001:2015")

    def test_create_certification(self):
        """Test creating a new certification."""
        data = {
            "organization": self.org.pk,
            "cert_body": self.cert_body.pk,
            "certificate_number": "CERT-API-002",
            "standard": "ISO 14001:2015",
            "scope": "Environmental Management System"
        }
        response = self.client.post(self.cert_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Certification.objects.count(), 2)
        new_cert = Certification.objects.get(certificate_number="CERT-API-002")
        self.assertEqual(new_cert.standard, "ISO 14001:2015")

    def test_update_certification(self):
        """Test updating a certification."""
        data = {
            "organization": self.org.pk,
            "cert_body": self.cert_body.pk,
            "certificate_number": "CERT-API-001-UPDATED",
            "standard": "ISO 9001:2015",
            "scope": "Updated Quality Management System"
        }
        response = self.client.put(self.cert_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.cert.refresh_from_db()
        self.assertEqual(self.cert.certificate_number, "CERT-API-001-UPDATED")
        self.assertEqual(self.cert.scope, "Updated Quality Management System")

    def test_delete_certification(self):
        """Test deleting a certification."""
        response = self.client.delete(self.cert_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Certification.objects.count(), 0)
        # cert should no longer exist
        with self.assertRaises(Certification.DoesNotExist):
            Certification.objects.get(pk=self.cert.pk)