# apps/certification_bodies/tests.py

"""
Unit tests for the Certification Bodies app.

This module contains test cases for the CertBody model, ensuring that
certification bodies can be created and validated correctly.
"""

# Suppress pylint no-member warnings for CertBody
# pylint: disable=no-member

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import CertBody, CertBodyUser, Auditor


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
        cert_body = CertBody.objects.create(
            name="QualityCert", 
            accreditation_id="ACB123",
            contact_email="info@qualitycert.org",
            is_active=True
        )
        self.assertEqual(cert_body.name, "QualityCert")
        self.assertEqual(cert_body.accreditation_id, "ACB123")
        self.assertEqual(cert_body.contact_email, "info@qualitycert.org")
        self.assertTrue(cert_body.is_active)

    def test_certbody_string_representation(self):
        """
        Test the string representation of a CertBody instance.
        """
        cert_body = CertBody.objects.create(
            name="StandardsChecker", 
            accreditation_id="SC456"
        )
        self.assertEqual(str(cert_body), "StandardsChecker")


class CertBodyViewTest(TestCase):
    """
    Test suite for the Certification Body views.
    """

    def setUp(self):
        self.cert_body = CertBody.objects.create(
            name="Test Cert Body",
            accreditation_id="TCB789"
        )

    def test_certbody_list_view(self):
        """
        Test the certification body list view.

        This test ensures that the certification body list view returns a 200 status code
        and contains the expected certification body data.
        """
        response = self.client.get(reverse("certification_bodies:certbody_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Cert Body")

    def test_certbody_detail_view(self):
        """
        Test the certification body detail view.

        This test ensures that the certification body detail view returns a 200 status code
        and contains the expected certification body data.
        """
        response = self.client.get(reverse("certification_bodies:certbody_detail", args=[self.cert_body.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Cert Body")


class CertBodyUserTest(TestCase):
    """
    Test suite for CertBodyUser model.
    """
    
    def setUp(self):
        self.cert_body = CertBody.objects.create(
            name="Certification Authority", 
            accreditation_id="CA123"
        )
        self.user = User.objects.create_user(
            username="cert_staff",
            email="staff@certauthority.com",
            password="password123"
        )
        
    def test_certbody_user_creation(self):
        """
        Test creating a user associated with a certification body.
        """
        staff = CertBodyUser.objects.create(
            user=self.user,
            cert_body=self.cert_body,
            role='admin'
        )
        
        self.assertEqual(staff.user, self.user)
        self.assertEqual(staff.cert_body, self.cert_body)
        self.assertEqual(staff.role, 'admin')
        self.assertTrue(staff.is_active)
        
    def test_certbody_user_roles(self):
        """
        Test different roles for certification body users.
        """
        roles = ['admin', 'auditor', 'secretary', 'accountant']
        
        for i, role in enumerate(roles):
            user = User.objects.create_user(
                username=f"staff_{role}",
                password="password"
            )
            staff = CertBodyUser.objects.create(
                user=user,
                cert_body=self.cert_body,
                role=role
            )
            self.assertEqual(staff.role, role)
            self.assertIn(role, str(staff))


class AuditorTest(TestCase):
    """
    Test suite for the Auditor model.
    """
    
    def setUp(self):
        self.cert_body1 = CertBody.objects.create(
            name="ISO Certification Body", 
            accreditation_id="ISO-CB"
        )
        self.cert_body2 = CertBody.objects.create(
            name="Security Certification Body", 
            accreditation_id="SEC-CB"
        )
        self.user = User.objects.create_user(
            username="qualified_auditor",
            email="auditor@example.com",
            password="password123"
        )
        
    def test_auditor_creation(self):
        """
        Test creating an auditor.
        """
        auditor = Auditor.objects.create(
            user=self.user,
            specialties="ISO 9001, ISO 14001",
            is_active=True
        )
        
        self.assertEqual(auditor.user, self.user)
        self.assertEqual(auditor.specialties, "ISO 9001, ISO 14001")
        self.assertTrue(auditor.is_active)
        
    def test_auditor_certification_bodies(self):
        """
        Test associating auditors with multiple certification bodies.
        """
        auditor = Auditor.objects.create(
            user=self.user,
            specialties="Multiple standards",
            is_active=True
        )
        
        # Associate with certification bodies
        auditor.cert_bodies.add(self.cert_body1)
        auditor.cert_bodies.add(self.cert_body2)
        
        self.assertEqual(auditor.cert_bodies.count(), 2)
        self.assertIn(self.cert_body1, auditor.cert_bodies.all())
        self.assertIn(self.cert_body2, auditor.cert_bodies.all())
