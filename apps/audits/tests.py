# apps/audits/tests.py

"""
Unit tests for the Audits app.

This module contains test cases for the Audit model and its functionality.
Expand these tests to cover additional scenarios and edge cases.
"""

from django.test import TestCase
from django.urls import reverse

from apps.audits.models import Audit
from apps.certification_bodies.models import CertBody
from apps.organizations.models import Organization


class AuditModelTest(TestCase):
    """
    Basic tests for the Audit model. Expand with real scenarios.
    """

    def setUp(self):
        """
        Set up test data for the Audit model.
        """
        # Create a test organization
        self.organization = Organization.objects.create(
            name="Test Organization", contact_email="test@organization.com"
        )

        # Create a test certification body
        self.cert_body = CertBody.objects.create(
            name="Test Certification Body", accreditation_id="ACB123"
        )

    def test_create_audit(self):
        """
        Test the creation of an Audit instance.
        """
        audit = Audit.objects.create(
            audit_type="Stage1",
            status="In Progress",
            organization=self.organization,
            certbody=self.cert_body,  # Assign the certbody
        )
        self.assertEqual(audit.audit_type, "Stage1")
        self.assertEqual(audit.status, "In Progress")
        self.assertEqual(audit.organization.name, "Test Organization")
        self.assertEqual(audit.certbody.name, "Test Certification Body")


class AuditViewTest(TestCase):
    def setUp(self):
        self.organization = Organization.objects.create(name="Test Org")
        self.cert_body = CertBody.objects.create(name="Test Cert Body")
        self.audit = Audit.objects.create(
            audit_type="Stage1",
            status="Scheduled",
            organization=self.organization,
            certbody=self.cert_body,
        )

    def test_audit_list_view(self):
        response = self.client.get(reverse("audit_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Stage1")

    def test_audit_detail_view(self):
        response = self.client.get(reverse("audit_detail", args=[self.audit.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Stage1")
