"""
Comprehensive tests for the organizations API.

This module contains extensive tests for the Organization API endpoints,
covering additional edge cases and authorization scenarios.
"""

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

User = get_user_model()

from apps.certification_bodies.models import CertBody
from apps.utils.test_credentials import get_test_credential

from .api_urls import router
from .api_views import CertificationViewSet, OrganizationViewSet
from .models import Certification, Organization, OrganizationUser
from .serializers import (
    CertificationSerializer,
    OrganizationDetailSerializer,
    OrganizationSerializer,
)


class OrganizationAPIURLsTest(TestCase):
    """Test suite for Organizations API URL patterns."""

    def test_organization_list_url(self):
        """Test organization list URL pattern."""
        url = reverse("organizations-api:organization-list")
        self.assertEqual(url, "/api/organizations/")
        resolver = resolve(url)
        self.assertEqual(resolver.func.__name__, "OrganizationViewSet")

    def test_organization_detail_url(self):
        """Test organization detail URL pattern."""
        url = reverse("organizations-api:organization-detail", args=[1])
        self.assertEqual(url, "/api/organizations/1/")
        resolver = resolve(url)
        self.assertEqual(resolver.func.__name__, "OrganizationViewSet")

    def test_certification_list_url(self):
        """Test certification list URL pattern."""
        url = reverse("organizations-api:certification-list")
        self.assertEqual(url, "/api/certifications/")
        resolver = resolve(url)
        self.assertEqual(resolver.func.__name__, "CertificationViewSet")


class OrganizationAPIPermissionsTest(APITestCase):
    """Test suite for API permissions."""

    def setUp(self):
        """Set up test data."""
        # Create users with different permission levels
        self.standard_user = User.objects.create_user(
            username=get_test_credential("default", "username"),
            password=get_test_credential("default", "password"),
            email=get_test_credential("default", "email"),
        )
        self.staff_user = User.objects.create_user(
            username=get_test_credential("staff", "username", "staff_user"),
            password=get_test_credential("staff", "password", "staff123"),
            email="staff@example.com",
            is_staff=True,
        )

        # Create an organization for testing
        self.organization = Organization.objects.create(
            name="Permission Test Org",
            industry="Technology",
            contact_email="permtest@example.com",
            is_active=True,
        )

        # URL for API calls
        self.organizations_url = reverse("organizations-api:organization-list")
        self.organization_detail_url = reverse(
            "organizations-api:organization-detail", args=[self.organization.pk]
        )

    def test_unauthenticated_access(self):
        """Test that unauthenticated users cannot access API."""
        # Get organizations (unauthenticated)
        response = self.client.get(self.organizations_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Get organization detail (unauthenticated)
        response = self.client.get(self.organization_detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Create organization (unauthenticated)
        data = {"name": "New Test Org", "industry": "Finance", "contact_email": "new@example.com"}
        response = self.client.post(self.organizations_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_access(self):
        """Test that authenticated users can access API."""
        # Login
        self.client.force_authenticate(user=self.standard_user)

        # Get organizations (authenticated)
        response = self.client.get(self.organizations_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Get organization detail (authenticated)
        response = self.client.get(self.organization_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class OrganizationAPIViewSetTest(APITestCase):
    """Comprehensive test suite for OrganizationViewSet."""

    def setUp(self):
        """Set up test data."""
        # Create user
        self.user = User.objects.create_user(
            username=get_test_credential("api", "username", "api_tester"),
            password=get_test_credential("api", "password", "complex123"),
            email=get_test_credential("api", "email", "api@example.com"),
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        # Create organizations
        self.organization1 = Organization.objects.create(
            name="API Test Org 1",
            industry="Technology",
            contact_email="test1@example.com",
            address="123 API Street",
            website="https://example1.com",
            is_active=True,
        )
        self.organization2 = Organization.objects.create(
            name="API Test Org 2",
            industry="Healthcare",
            contact_email="test2@example.com",
            address="456 API Avenue",
            website="https://example2.com",
            is_active=True,
        )

        # Create organization user association
        self.org_user = OrganizationUser.objects.create(
            user=self.user, organization=self.organization1, role="admin"
        )

        # Create cert body
        self.cert_body = CertBody.objects.create(
            name="API Test CB", accreditation_id="ATCB-123", is_active=True
        )

        # Create certification
        self.certification = Certification.objects.create(
            organization=self.organization1,
            certificate_number="API-TEST-123",
            standard="ISO 9001:2015",
            issue_date=timezone.now().date(),
            expiry_date=timezone.now().date() + timedelta(days=365 * 3),
            cert_body=self.cert_body,
            scope="API Test Certification",
        )

        # API URLs
        self.organization_list_url = reverse("organizations-api:organization-list")
        self.organization_detail_url = reverse(
            "organizations-api:organization-detail", args=[self.organization1.pk]
        )
        self.organization_certifications_url = reverse(
            "organizations-api:organization-certifications", args=[self.organization1.pk]
        )

    def test_get_organization_list(self):
        """Test retrieving a list of organizations."""
        response = self.client.get(self.organization_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        # Check serializer class used
        organizations = Organization.objects.all()
        serializer = OrganizationSerializer(organizations, many=True)
        self.assertEqual(response.data, serializer.data)

    def test_get_organization_detail(self):
        """Test retrieving organization detail."""
        response = self.client.get(self.organization_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that detail serializer is used
        organization = Organization.objects.get(pk=self.organization1.pk)
        serializer = OrganizationDetailSerializer(organization)
        self.assertEqual(response.data, serializer.data)

    def test_create_organization(self):
        """Test creating a new organization."""
        data = {
            "name": "New API Organization",
            "industry": "Finance",
            "contact_email": "newapi@example.com",
            "address": "789 API Boulevard",
            "website": "https://newapi.com",
            "is_active": True,
        }
        response = self.client.post(self.organization_list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify organization was created
        self.assertTrue(Organization.objects.filter(name="New API Organization").exists())

    def test_update_organization(self):
        """Test updating an organization."""
        data = {
            "name": "Updated API Organization",
            "industry": "Technology",
            "contact_email": "updated@example.com",
            "is_active": True,
        }
        response = self.client.put(self.organization_detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify organization was updated
        self.organization1.refresh_from_db()
        self.assertEqual(self.organization1.name, "Updated API Organization")
        self.assertEqual(self.organization1.contact_email, "updated@example.com")

    def test_partial_update_organization(self):
        """Test partially updating an organization."""
        data = {"name": "Partially Updated Org"}
        response = self.client.patch(self.organization_detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify only the specified field was updated
        self.organization1.refresh_from_db()
        self.assertEqual(self.organization1.name, "Partially Updated Org")
        self.assertEqual(self.organization1.contact_email, "test1@example.com")  # Unchanged

    def test_delete_organization(self):
        """Test deleting an organization."""
        response = self.client.delete(self.organization_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verify organization was deleted
        self.assertFalse(Organization.objects.filter(pk=self.organization1.pk).exists())

    def test_organization_certifications_action(self):
        """Test the certifications custom action."""
        response = self.client.get(self.organization_certifications_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Should contain only certs for this org
        certs = self.organization1.certifications.all()
        serializer = CertificationSerializer(certs, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(len(response.data), 1)


class CertificationAPIViewSetTest(APITestCase):
    """Comprehensive test suite for CertificationViewSet."""

    def setUp(self):
        """Set up test data."""
        # Create user
        self.user = User.objects.create_user(
            username=get_test_credential("api_alt", "username", "cert_api_tester"),
            password=get_test_credential("api_alt", "password", "complex123"),
            email=get_test_credential("api_alt", "email", "certapi@example.com"),
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        # Create organization and cert body
        self.organization = Organization.objects.create(
            name="Cert API Test Org",
            industry="Technology",
            contact_email="certtest@example.com",
            is_active=True,
        )
        self.cert_body = CertBody.objects.create(
            name="Cert API CB", accreditation_id="CACB-456", is_active=True
        )

        # Create certification
        self.certification = Certification.objects.create(
            organization=self.organization,
            certificate_number="CERT-API-TEST-123",
            standard="ISO 27001:2022",
            issue_date=timezone.now().date(),
            expiry_date=timezone.now().date() + timedelta(days=365 * 3),
            cert_body=self.cert_body,
            scope="Cert API Test Certification",
        )

        # API URLs
        self.certification_list_url = reverse("organizations-api:certification-list")
        self.certification_detail_url = reverse(
            "organizations-api:certification-detail", args=[self.certification.pk]
        )

    def test_get_certification_list(self):
        """Test retrieving a list of certifications."""
        response = self.client.get(self.certification_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        # Check serializer data
        certs = Certification.objects.all()
        serializer = CertificationSerializer(certs, many=True)
        self.assertEqual(response.data, serializer.data)

    def test_get_certification_detail(self):
        """Test retrieving certification detail."""
        response = self.client.get(self.certification_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check serialized data
        certification = Certification.objects.get(pk=self.certification.pk)
        serializer = CertificationSerializer(certification)
        self.assertEqual(response.data, serializer.data)

    def test_create_certification(self):
        """Test creating a new certification."""
        today = timezone.now().date()
        data = {
            "organization": self.organization.pk,
            "certificate_number": "NEW-CERT-API-789",
            "standard": "ISO 14001:2015",
            "issue_date": today.isoformat(),
            "expiry_date": (today + timedelta(days=365 * 3)).isoformat(),
            "cert_body": self.cert_body.pk,
            "scope": "Environmental Management System",
        }
        response = self.client.post(self.certification_list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify certification was created
        self.assertTrue(
            Certification.objects.filter(certificate_number="NEW-CERT-API-789").exists()
        )

    def test_update_certification(self):
        """Test updating an certification."""
        today = timezone.now().date()
        data = {
            "organization": self.organization.pk,
            "certificate_number": "UPDATED-CERT-API",
            "standard": "ISO 27001:2022",
            "issue_date": today.isoformat(),
            "expiry_date": (today + timedelta(days=365 * 3)).isoformat(),
            "cert_body": self.cert_body.pk,
            "scope": "Updated Information Security Management",
        }
        response = self.client.put(self.certification_detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify certification was updated
        self.certification.refresh_from_db()
        self.assertEqual(self.certification.certificate_number, "UPDATED-CERT-API")
        self.assertEqual(self.certification.scope, "Updated Information Security Management")

    def test_partial_update_certification(self):
        """Test partially updating a certification."""
        data = {"scope": "Partially Updated Scope"}
        response = self.client.patch(self.certification_detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify only the specified field was updated
        self.certification.refresh_from_db()
        self.assertEqual(self.certification.scope, "Partially Updated Scope")
        self.assertEqual(self.certification.certificate_number, "CERT-API-TEST-123")  # Unchanged

    def test_delete_certification(self):
        """Test deleting a certification."""
        response = self.client.delete(self.certification_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verify certification was deleted
        self.assertFalse(Certification.objects.filter(pk=self.certification.pk).exists())
