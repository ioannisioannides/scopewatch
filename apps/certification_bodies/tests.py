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
from django.utils import timezone
from datetime import timedelta

from apps.audits.models import Audit, AuditResult
from apps.organizations.models import Organization, Certification
from .models import CertBody, CertBodyUser, Auditor
from .forms import CertificationIssueForm, AuditDecisionForm


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
            is_active=True,
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
            name="StandardsChecker", accreditation_id="SC456"
        )
        self.assertEqual(str(cert_body), "StandardsChecker")


class CertBodyViewTest(TestCase):
    """
    Test suite for the Certification Body views.
    """

    def setUp(self):
        self.cert_body = CertBody.objects.create(
            name="Test Cert Body", accreditation_id="TCB789"
        )
        # Create a user for authenticated views
        self.user = User.objects.create_user(
            username="certbody_staff", 
            email="staff@certbody.com", 
            password="secure_password123"
        )
        self.cert_body_user = CertBodyUser.objects.create(
            user=self.user,
            cert_body=self.cert_body,
            role="admin",
            is_active=True
        )
        # Create organization for audits
        self.organization = Organization.objects.create(
            name="Test Organization",
            industry="Manufacturing",
            is_active=True
        )
        # Create audit for testing decisions
        self.audit = Audit.objects.create(
            organization=self.organization,
            certbody=self.cert_body,
            audit_type="initial",
            status="completed",
            standard="ISO 9001:2015",
            scheduled_date=timezone.now().date()
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
        response = self.client.get(
            reverse("certification_bodies:certbody_detail", args=[self.cert_body.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Cert Body")

    def test_audit_pending_decision_list_view_unauthenticated(self):
        """
        Test that unauthenticated users are redirected from the pending decision list view.
        """
        response = self.client.get(reverse("certification_bodies:pending_decisions"))
        # Should redirect to login page
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_audit_pending_decision_list_view_authenticated(self):
        """
        Test that authenticated cert body users can see the pending decision list view.
        """
        self.client.login(username="certbody_staff", password="secure_password123")
        response = self.client.get(reverse("certification_bodies:pending_decisions"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Pending Decisions")

    def test_audit_pending_decision_list_contains_audits(self):
        """
        Test that the pending decision list shows audits that need decisions.
        """
        self.client.login(username="certbody_staff", password="secure_password123")
        response = self.client.get(reverse("certification_bodies:pending_decisions"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("audits", response.context)
        self.assertEqual(list(response.context["audits"]), [self.audit])

    def test_audit_decision_view_unauthorized(self):
        """
        Test that unauthorized users cannot access the audit decision view.
        """
        # Create another cert body and user that shouldn't have access
        other_cert_body = CertBody.objects.create(
            name="Other Cert Body", accreditation_id="OCB123"
        )
        other_user = User.objects.create_user(
            username="other_staff", password="other_password"
        )
        CertBodyUser.objects.create(
            user=other_user, cert_body=other_cert_body, is_active=True
        )
        
        self.client.login(username="other_staff", password="other_password")
        response = self.client.get(
            reverse("certification_bodies:audit_decision", args=[self.audit.pk])
        )
        # Should redirect with an error message
        self.assertEqual(response.status_code, 302)

    def test_audit_decision_view_authorized(self):
        """
        Test that authorized users can access the audit decision view.
        """
        self.client.login(username="certbody_staff", password="secure_password123")
        response = self.client.get(
            reverse("certification_bodies:audit_decision", args=[self.audit.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Audit Decision")
        self.assertIsInstance(response.context["form"], AuditDecisionForm)

    def test_audit_decision_submission(self):
        """
        Test that submitting an audit decision works correctly.
        """
        self.client.login(username="certbody_staff", password="secure_password123")
        response = self.client.post(
            reverse("certification_bodies:audit_decision", args=[self.audit.pk]),
            {
                "decision": "approve",
                "comments": "Looks good, approved.",
            }
        )
        # Should redirect to certificate issuance page
        self.assertEqual(response.status_code, 302)
        
        # Check that audit result was created
        audit_result = AuditResult.objects.filter(audit=self.audit).first()
        self.assertIsNotNone(audit_result)
        self.assertEqual(audit_result.decision, "approve")
        self.assertEqual(audit_result.comments, "Looks good, approved.")

    def test_issue_certificate_view_unauthorized(self):
        """
        Test that unauthorized users cannot issue certificates.
        """
        # Create an approved audit result first
        audit_result = AuditResult.objects.create(
            audit=self.audit,
            decision="approve",
            comments="Approved for certification",
            decided_by=self.cert_body_user
        )
        
        # Try to access with an unauthorized user
        other_user = User.objects.create_user(
            username="unauthorized", password="password123"
        )
        self.client.login(username="unauthorized", password="password123")
        response = self.client.get(
            reverse("certification_bodies:issue_certificate", args=[self.audit.pk])
        )
        self.assertEqual(response.status_code, 302)  # Should redirect

    def test_issue_certificate_view_authorized(self):
        """
        Test that authorized users can access the certificate issuance view.
        """
        # Create an approved audit result first
        audit_result = AuditResult.objects.create(
            audit=self.audit,
            decision="approve",
            comments="Approved for certification",
            decided_by=self.cert_body_user
        )
        
        self.client.login(username="certbody_staff", password="secure_password123")
        response = self.client.get(
            reverse("certification_bodies:issue_certificate", args=[self.audit.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Issue Certificate")
        self.assertIsInstance(response.context["form"], CertificationIssueForm)

    def test_issue_certificate_submission(self):
        """
        Test that submitting a certificate issuance form works correctly.
        """
        # Create an approved audit result first
        audit_result = AuditResult.objects.create(
            audit=self.audit,
            decision="approve",
            comments="Approved for certification",
            decided_by=self.cert_body_user
        )
        
        self.client.login(username="certbody_staff", password="secure_password123")
        response = self.client.post(
            reverse("certification_bodies:issue_certificate", args=[self.audit.pk]),
            {
                "certificate_number": "CERT-123",
                "scope": "Quality Management System",
                "expiry_date": (timezone.now().date() + timedelta(days=365*3)).strftime('%Y-%m-%d'),
            }
        )
        
        # Check that certificate was created
        cert = Certification.objects.filter(audit=self.audit).first()
        self.assertIsNotNone(cert)
        self.assertEqual(cert.certificate_number, "CERT-123")
        self.assertEqual(cert.scope, "Quality Management System")


class CertBodyUserTest(TestCase):
    """
    Test suite for CertBodyUser model.
    """

    def setUp(self):
        self.cert_body = CertBody.objects.create(
            name="Certification Authority", accreditation_id="CA123"
        )
        self.user = User.objects.create_user(
            username="cert_staff",
            email="staff@certauthority.com",
            password="password123",
        )

    def test_certbody_user_creation(self):
        """
        Test creating a user associated with a certification body.
        """
        staff = CertBodyUser.objects.create(
            user=self.user, cert_body=self.cert_body, role="admin"
        )

        self.assertEqual(staff.user, self.user)
        self.assertEqual(staff.cert_body, self.cert_body)
        self.assertEqual(staff.role, "admin")
        self.assertTrue(staff.is_active)

    def test_certbody_user_roles(self):
        """
        Test different roles for certification body users.
        """
        roles = ["admin", "auditor", "secretary", "accountant"]

        for i, role in enumerate(roles):
            user = User.objects.create_user(
                username=f"staff_{role}", password="password"
            )
            staff = CertBodyUser.objects.create(
                user=user, cert_body=self.cert_body, role=role
            )
            self.assertEqual(staff.role, role)
            self.assertIn(role, str(staff))


class AuditorTest(TestCase):
    """
    Test suite for the Auditor model.
    """

    def setUp(self):
        self.cert_body1 = CertBody.objects.create(
            name="ISO Certification Body", accreditation_id="ISO-CB"
        )
        self.cert_body2 = CertBody.objects.create(
            name="Security Certification Body", accreditation_id="SEC-CB"
        )
        self.user = User.objects.create_user(
            username="qualified_auditor",
            email="auditor@example.com",
            password="password123",
        )

    def test_auditor_creation(self):
        """
        Test creating an auditor.
        """
        auditor = Auditor.objects.create(
            user=self.user, specialties="ISO 9001, ISO 14001", is_active=True
        )

        self.assertEqual(auditor.user, self.user)
        self.assertEqual(auditor.specialties, "ISO 9001, ISO 14001")
        self.assertTrue(auditor.is_active)

    def test_auditor_certification_bodies(self):
        """
        Test associating auditors with multiple certification bodies.
        """
        auditor = Auditor.objects.create(
            user=self.user, specialties="Multiple standards", is_active=True
        )

        # Associate with certification bodies
        auditor.cert_bodies.add(self.cert_body1)
        auditor.cert_bodies.add(self.cert_body2)

        self.assertEqual(auditor.cert_bodies.count(), 2)
        self.assertIn(self.cert_body1, auditor.cert_bodies.all())
        self.assertIn(self.cert_body2, auditor.cert_bodies.all())
