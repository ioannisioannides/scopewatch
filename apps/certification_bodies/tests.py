# apps/certification_bodies/tests.py

"""
Unit tests for the Certification Bodies app.

This module contains test cases for the CertBody model, ensuring that
certification bodies can be created and validated correctly.
"""

# Suppress pylint no-member warnings for CertBody
# pylint: disable=no-member

from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from apps.audits.models import Audit, AuditResult
from apps.organizations.models import Organization, Certification
from apps.utils.test_credentials import get_test_credential
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
        # Create a user for authenticated views using environment variables
        self.user = User.objects.create_user(
            username=get_test_credential("certbody", "username"),
            email=get_test_credential("certbody", "email"),
            password=get_test_credential("certbody", "password")
        )
        self.cert_body_user = CertBodyUser.objects.create(
            user=self.user,
            cert_body=self.cert_body,
            role="admin",
            is_active=True
        )
        self.client = Client()
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
        self.client.login(
            username=get_test_credential("certbody", "username"),
            password=get_test_credential("certbody", "password")
        )
        response = self.client.get(reverse("certification_bodies:pending_decisions"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Pending Decisions")

    def test_audit_pending_decision_list_contains_audits(self):
        """
        Test that the pending decision list shows audits that need decisions.
        """
        self.client.login(
            username=get_test_credential("certbody", "username"),
            password=get_test_credential("certbody", "password")
        )
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
            username=get_test_credential("unauthorized", "username"),
            password=get_test_credential("unauthorized", "password")
        )
        CertBodyUser.objects.create(
            user=other_user, cert_body=other_cert_body, is_active=True
        )
        
        self.client.login(
            username=get_test_credential("unauthorized", "username"),
            password=get_test_credential("unauthorized", "password")
        )
        response = self.client.get(
            reverse("certification_bodies:audit_decision", args=[self.audit.pk])
        )
        # Should redirect with an error message
        self.assertEqual(response.status_code, 302)

    def test_audit_decision_view_authorized(self):
        """
        Test that authorized users can access the audit decision view.
        """
        self.client.login(
            username=get_test_credential("certbody", "username"),
            password=get_test_credential("certbody", "password")
        )
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
        self.client.login(
            username=get_test_credential("certbody", "username"),
            password=get_test_credential("certbody", "password")
        )
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
            username=get_test_credential("unauthorized", "username"),
            password=get_test_credential("unauthorized", "password")
        )
        self.client.login(
            username=get_test_credential("unauthorized", "username"),
            password=get_test_credential("unauthorized", "password")
        )
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
        
        self.client.login(
            username=get_test_credential("certbody", "username"),
            password=get_test_credential("certbody", "password")
        )
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
        
        self.client.login(
            username=get_test_credential("certbody", "username"),
            password=get_test_credential("certbody", "password")
        )
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


class ExtendedCertBodyViewTest(TestCase):
    """
    Additional test suite for edge cases in Certification Body views.
    """

    def setUp(self):
        # Create cert body, user, and organization
        self.cert_body = CertBody.objects.create(
            name="Edge Case Cert Body", accreditation_id="ECCB123"
        )
        self.user = User.objects.create_user(
            username="cert_tester", email="tester@certbody.com", password="testpass123"
        )
        self.cert_body_user = CertBodyUser.objects.create(
            user=self.user,
            cert_body=self.cert_body,
            role="admin",
            is_active=True
        )
        self.organization = Organization.objects.create(
            name="Test Org", industry="Technology", is_active=True
        )
        self.audit = Audit.objects.create(
            organization=self.organization,
            certbody=self.cert_body,
            audit_type="initial",
            status="completed",
            standard="ISO 27001",
            scheduled_date=timezone.now().date()
        )
        
        # Create second cert body and user for unauthorized tests
        self.other_cert_body = CertBody.objects.create(
            name="Other Cert Body", accreditation_id="OTHER123"
        )
        self.other_user = User.objects.create_user(
            username="other_tester", email="other@certbody.com", password="otherpass123"
        )
        self.other_cert_body_user = CertBodyUser.objects.create(
            user=self.other_user,
            cert_body=self.other_cert_body,
            role="admin",
            is_active=True
        )
        
    def test_pending_decision_list_no_cert_body_user(self):
        """
        Test pending decision list when user has no certification body association.
        """
        # Create user with no cert body association
        user_no_cert = User.objects.create_user(
            username="no_cert_user", password="password123"
        )
        
        self.client.login(username="no_cert_user", password="password123")
        response = self.client.get(reverse("certification_bodies:pending_decisions"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("audits", response.context)
        self.assertEqual(len(response.context["audits"]), 0)  # Should show no audits
    
    def test_audit_decision_view_exception_handling(self):
        """
        Test that the audit decision view handles exceptions properly.
        """
        # Login with an unrelated user (no cert body associations)
        unrelated_user = User.objects.create_user(
            username="unrelated", password="unrelated123"
        )
        self.client.login(username="unrelated", password="unrelated123")
        
        # Access audit decision view without proper permissions
        response = self.client.get(
            reverse("certification_bodies:audit_decision", args=[self.audit.pk])
        )
        
        # Should redirect to dashboard with error message
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("certification_bodies:dashboard"))
    
    def test_audit_decision_submission_followup(self):
        """
        Test submitting a 'followup' audit decision.
        """
        self.client.login(username="cert_tester", password="testpass123")
        response = self.client.post(
            reverse("certification_bodies:audit_decision", args=[self.audit.pk]),
            {
                "decision": "followup",
                "comments": "Needs follow-up actions before approval",
            }
        )
        
        # Should redirect to pending decisions page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("certification_bodies:pending_decisions"))
        
        # Verify audit status changed to in_progress
        self.audit.refresh_from_db()
        self.assertEqual(self.audit.status, "in_progress")
        
        # Check that audit result was created
        audit_result = AuditResult.objects.filter(audit=self.audit).first()
        self.assertEqual(audit_result.decision, "followup")
    
    def test_issue_certificate_invalid_audit_status(self):
        """
        Test issue certificate view with invalid audit status.
        """
        # Create audit with invalid status
        invalid_audit = Audit.objects.create(
            organization=self.organization,
            certbody=self.cert_body,
            audit_type="initial",
            status="in_progress",  # Not completed
            standard="ISO 9001",
            scheduled_date=timezone.now().date()
        )
        
        self.client.login(username="cert_tester", password="testpass123")
        
        # Try to issue certificate for invalid audit (no result yet)
        response = self.client.get(
            reverse("certification_bodies:issue_certificate", args=[invalid_audit.pk])
        )
        
        # Should redirect with error
        self.assertEqual(response.status_code, 302)
    
    def test_issue_certificate_with_rejected_result(self):
        """
        Test attempt to issue certificate with rejected audit result.
        """
        # Create audit result with rejection
        audit_result = AuditResult.objects.create(
            audit=self.audit,
            decision="reject",
            comments="Does not meet standards",
            decided_by=self.cert_body_user
        )
        
        self.client.login(username="cert_tester", password="testpass123")
        response = self.client.get(
            reverse("certification_bodies:issue_certificate", args=[self.audit.pk])
        )
        
        # Should redirect with error
        self.assertEqual(response.status_code, 302)
    
    def test_issue_certificate_already_exists(self):
        """
        Test when trying to issue a certificate that already exists.
        """
        # Create approved audit result
        audit_result = AuditResult.objects.create(
            audit=self.audit,
            decision="approve",
            comments="Approved",
            decided_by=self.cert_body_user
        )
        
        # Create existing certification
        existing_cert = Certification.objects.create(
            organization=self.organization,
            standard=self.audit.standard,
            certificate_number="EXISTING-123",
            issue_date=timezone.now().date(),
            expiry_date=timezone.now().date() + timedelta(days=365*3),
            audit=self.audit,
            scope="Existing certification scope"
        )
        
        self.client.login(username="cert_tester", password="testpass123")
        response = self.client.get(
            reverse("certification_bodies:issue_certificate", args=[self.audit.pk])
        )
        
        # Should redirect to the existing certification
        self.assertEqual(response.status_code, 302)
    
    def test_issue_certificate_form_validation_error(self):
        """
        Test form validation error when issuing a certificate.
        """
        # Create approved audit result
        audit_result = AuditResult.objects.create(
            audit=self.audit,
            decision="approve",
            comments="Approved",
            decided_by=self.cert_body_user
        )
        
        self.client.login(username="cert_tester", password="testpass123")
        
        # Submit with invalid certificate number (empty)
        response = self.client.post(
            reverse("certification_bodies:issue_certificate", args=[self.audit.pk]),
            {
                "certificate_number": "",  # Invalid - should be required
                "scope": "Test scope",
                "expiry_date": (timezone.now().date() + timedelta(days=365*3)).strftime('%Y-%m-%d'),
            }
        )
        
        # Should stay on the form with errors
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "field is required")
