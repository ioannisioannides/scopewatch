# apps/organizations/tests.py

from django.test import TestCase
from .models import Organization

class OrganizationModelTest(TestCase):
    """
    Basic tests for the Organization model.
    """
    def test_create_organization(self):
        org = Organization.objects.create(
            name="TestOrg",
            contact_email="contact@testorg.com"
        )
        self.assertEqual(org.name, "TestOrg")
        self.assertEqual(org.contact_email, "contact@testorg.com")
        self.assertTrue(org.is_active)
