# apps/organizations/tests.py

"""
Unit tests for the Organizations app.

This module contains test cases for the Organization model and its functionality.
Expand these tests to cover additional scenarios and edge cases.
"""

from django.test import TestCase
from django.urls import reverse

from .models import Organization


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
            name="TestOrg",
            contact_email="contact@testorg.com"
        )
        self.assertEqual(org.name, "TestOrg")
        self.assertEqual(org.contact_email, "contact@testorg.com")
        self.assertTrue(org.is_active)

class OrganizationViewTest(TestCase):
    def setUp(self):
        self.organization = Organization.objects.create(name="Test Org")

    def test_organization_list_view(self):
        response = self.client.get(reverse('organization_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Org")

    def test_organization_detail_view(self):
        response = self.client.get(reverse('organization_detail', args=[self.organization.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Org")
