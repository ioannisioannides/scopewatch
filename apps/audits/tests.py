# apps/audits/tests.py

"""
Unit tests for the Audits app.

This module contains test cases for the Audit model and its functionality.
Expand these tests to cover additional scenarios and edge cases.
"""

from django.test import TestCase
from apps.audits.models import Audit
from apps.organizations.models import Organization
from apps.certification_bodies.models import CertBody

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
            name="Test Organization",
            contact_email="test@organization.com"
        )

        # Create a test certification body
        self.cert_body = CertBody.objects.create(
            name="Test Certification Body",
            accreditation_id="ACB123"
        )

    def test_create_audit(self):
        """
        Test the creation of an Audit instance.
        """
        audit = Audit.objects.create(
            audit_type="Stage1",
            status="In Progress",
            organization=self.organization,
            certbody=self.cert_body  # Assign the certbody
        )
        self.assertEqual(audit.audit_type, "Stage1")
        self.assertEqual(audit.status, "In Progress")
        self.assertEqual(audit.organization.name, "Test Organization")
        self.assertEqual(audit.certbody.name, "Test Certification Body")
