# apps/audits/tests.py

"""
Unit tests for the Audits app.

This module contains test cases for the Audit model and its functionality.
Expand these tests to cover additional scenarios and edge cases.
"""

from django.test import TestCase
from .models import Audit

class AuditModelTest(TestCase):
    """
    Basic tests for the Audit model. Expand with real scenarios.
    """
    def test_create_audit(self):
        audit = Audit.objects.create(audit_type="Stage1", status="In Progress")
        self.assertEqual(audit.audit_type, "Stage1")
        self.assertEqual(audit.status, "In Progress")
