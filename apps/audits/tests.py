# apps/audits/tests.py

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
