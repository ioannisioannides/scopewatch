# apps/certification_bodies/tests.py

from django.test import TestCase
from .models import CertBody

class CertBodyModelTest(TestCase):
    """
    Basic tests for the CertBody model.
    Expand with real scenarios.
    """
    def test_create_certbody(self):
        cb = CertBody.objects.create(name="QualityCert", accreditation_id="ACB123")
        self.assertEqual(cb.name, "QualityCert")
        self.assertEqual(cb.accreditation_id, "ACB123")
        self.assertTrue(cb.is_active)
