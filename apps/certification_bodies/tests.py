# apps/certification_bodies/tests.py

"""
Unit tests for the Certification Bodies app.

This module contains test cases for the CertBody model, ensuring that
certification bodies can be created and validated correctly.
"""

from django.test import TestCase
from django.urls import reverse
from .models import CertBody

class CertBodyModelTest(TestCase):
    """
    Test suite for the CertBody model.

    This class contains unit tests for creating and validating instances
    of the CertBody model.
    """

    def test_create_cert_body(self):
        """
        Test the creation of a CertBody instance.

        This test ensures that a CertBody instance can be created with valid data
        and that its attributes are correctly set.
        """
        cert_body = CertBody.objects.create(name="QualityCert", accreditation_id="ACB123")
        self.assertEqual(cert_body.name, "QualityCert")
        self.assertEqual(cert_body.accreditation_id, "ACB123")
        self.assertTrue(cert_body.is_active)

class CertBodyViewTest(TestCase):
    def setUp(self):
        self.cert_body = CertBody.objects.create(name="Test Cert Body")

    def test_certbody_list_view(self):
        response = self.client.get(reverse('certbody_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Cert Body")

    def test_certbody_detail_view(self):
        response = self.client.get(reverse('certbody_detail', args=[self.cert_body.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Cert Body")
