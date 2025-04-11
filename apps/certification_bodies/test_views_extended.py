"""
Comprehensive tests for the Certification Bodies app views.

This module focuses on improving test coverage for views in the certification_bodies app,
particularly targeting edge cases and error handling paths.
"""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone

from apps.audits.models import Audit, AuditResult, NonConformance
from apps.organizations.models import Certification, Organization

from .models import CertBody, CertBodyUser

User = get_user_model()


class ViewsTestCase(TestCase):
    """Comprehensive test suite for certification_bodies views."""

    def setUp(self):
        """Set up test data."""
        # Create certification body
        self.cert_body = CertBody.objects.create(
            name="Comprehensive Test CB",
            accreditation_id="CTCB-123",
            contact_email="test@certbody.com",
            is_active=True,
        )

        # Create users
        self.admin_user = User.objects.create_user(
            username="admin_user", password="secure_password", email="admin@example.com"
        )
        self.auditor_user = User.objects.create_user(
            username="auditor_user",
            password="secure_password",
            email="auditor@example.com",
        )
        self.unauthorized_user = User.objects.create_user(
            username="unauthorized",
            password="secure_password",
            email="unauthorized@example.com",
        )

        # Create cert body users
        self.admin_cb_user = CertBodyUser.objects.create(
            user=self.admin_user, cert_body=self.cert_body, role="admin", is_active=True
        )
        self.auditor_cb_user = CertBodyUser.objects.create(
            user=self.auditor_user,
            cert_body=self.cert_body,
            role="auditor",
            is_active=True,
        )

        # Create another certification body for testing unauthorized access
        self.other_cert_body = CertBody.objects.create(
            name="Other CB",
            accreditation_id="OCB-456",
            is_active=True,
        )

        # Create organization
        self.organization = Organization.objects.create(
            name="Test Organization",
            industry="Technology",
            contact_email="org@example.com",
            is_active=True,
        )

        # Create audits with different statuses
        today = timezone.now().date()

        self.completed_audit = Audit.objects.create(
            organization=self.organization,
            certbody=self.cert_body,
            audit_type="initial",
            status="completed",  # Completed but no decision yet
            standard="ISO 9001:2015",
            scheduled_date=today - timedelta(days=30),
        )

        self.in_progress_audit = Audit.objects.create(
            organization=self.organization,
            certbody=self.cert_body,
            audit_type="surveillance",
            status="in_progress",
            standard="ISO 9001:2015",
            scheduled_date=today - timedelta(days=7),
        )

        # Create nonconformances
        self.nonconformance = NonConformance.objects.create(
            audit=self.completed_audit,
            description="Test nonconformance",
            severity="minor",
        )

        # Set up request factory for view testing
        self.factory = RequestFactory()

    def setup_request_messages(self, request):
        """Set up request messages middleware."""
        setattr(request, "session", "session")
        messages = FallbackStorage(request)
        setattr(request, "_messages", messages)
        return request

    def test_audit_pending_decision_list_view_exception_handling(self):
        """Test AuditPendingDecisionListView exception handling."""
        # Remove attributes to force exception
        # This test confirms that exception handling in the view returns an empty queryset
        _original_user = self.admin_user

        url = reverse("certification_bodies:pending_decisions")
        self.client.force_login(self.unauthorized_user)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["audits"]), [])

    def test_audit_decision_view_with_complete_workflow(self):
        """Test the full workflow of making an audit decision."""
        # Login
        self.client.force_login(self.admin_user)

        # Get the audit decision form
        url = reverse("certification_bodies:audit_decision", args=[self.completed_audit.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "certification_bodies/audit_decision.html")
        self.assertContains(response, "Test nonconformance")  # Should show nonconformances

        # Submit the form with 'conditional' approval
        data = {
            "decision": "conditional",
            "comments": "Approved with conditions",
        }
        response = self.client.post(url, data)

        # Should redirect to certificate issuance
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            reverse("certification_bodies:issue_certificate", args=[self.completed_audit.pk]),
        )

        # Check if audit status was updated
        self.completed_audit.refresh_from_db()
        self.assertEqual(self.completed_audit.status, "closed")

        # Check if audit result was created
        audit_result = AuditResult.objects.filter(audit=self.completed_audit).first()
        self.assertIsNotNone(audit_result)
        self.assertEqual(audit_result.decision, "conditional")
        self.assertEqual(audit_result.comments, "Approved with conditions")
        self.assertEqual(audit_result.decided_by, self.admin_cb_user)

    def test_audit_decision_view_with_reject_decision(self):
        """Test handling of rejected audit decision."""
        self.client.force_login(self.admin_user)

        url = reverse("certification_bodies:audit_decision", args=[self.completed_audit.pk])
        data = {
            "decision": "reject",
            "comments": "Rejected due to critical issues",
        }
        response = self.client.post(url, data)

        # Should redirect to pending decisions (not certificate issuance)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("certification_bodies:pending_decisions"))

        # Audit status should be closed
        self.completed_audit.refresh_from_db()
        self.assertEqual(self.completed_audit.status, "closed")

        audit_result = AuditResult.objects.get(audit=self.completed_audit)
        self.assertEqual(audit_result.decision, "reject")
        self.assertFalse(audit_result.can_issue_certificate())

    def test_issue_certificate_view_complete_workflow(self):
        """Test the complete workflow for issuing a certificate."""
        # First create an approved audit result
        _audit_result = AuditResult.objects.create(
            audit=self.completed_audit,
            decision="approve",
            comments="Approved without conditions",
            decided_by=self.admin_cb_user,
        )

        # Login as admin user
        self.client.force_login(self.admin_user)

        # Get the certificate issuance form
        url = reverse("certification_bodies:issue_certificate", args=[self.completed_audit.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "certification_bodies/issue_certificate.html")

        # Submit the form
        today = timezone.now().date()
        data = {
            "certificate_number": "TEST-CERT-12345",
            "scope": "Complete test certification scope",
            "expiry_date": (today + timedelta(days=365 * 3)).strftime("%Y-%m-%d"),
        }
        response = self.client.post(url, data)

        # Should create a certificate and redirect to its detail page
        self.assertEqual(response.status_code, 302)

        # Check if certificate was created
        cert = Certification.objects.filter(certificate_number="TEST-CERT-12345").first()
        self.assertIsNotNone(cert)
        self.assertEqual(cert.organization, self.organization)
        self.assertEqual(cert.standard, self.completed_audit.standard)
        self.assertEqual(cert.cert_body, self.cert_body)

    def test_issue_certificate_with_invalid_form(self):
        """Test certificate issuance with invalid form data."""
        # Create approved audit result
        _audit_result = AuditResult.objects.create(
            audit=self.completed_audit,
            decision="approve",
            comments="Approved without conditions",
            decided_by=self.admin_cb_user,
        )

        self.client.force_login(self.admin_user)

        # Submit invalid form (missing certificate number)
        url = reverse("certification_bodies:issue_certificate", args=[self.completed_audit.pk])
        today = timezone.now().date()
        data = {
            "certificate_number": "",  # Invalid - empty
            "scope": "Test scope",
            "expiry_date": (today + timedelta(days=365 * 3)).strftime("%Y-%m-%d"),
        }
        response = self.client.post(url, data)

        # Should stay on the form with errors
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, "form", "certificate_number", "This field is required.")

    def test_issue_certificate_value_error(self):
        """Test handling of ValueError during certificate issuance."""
        # Create approved audit result
        _audit_result = AuditResult.objects.create(
            audit=self.completed_audit,
            decision="approve",
            comments="Approved without conditions",
            decided_by=self.admin_cb_user,
        )

        # Create a certification with the same certificate number we'll try to use
        _existing_cert = Certification.objects.create(
            organization=self.organization,
            certificate_number="DUPLICATE-NUMBER",
            standard=self.completed_audit.standard,
            issue_date=timezone.now().date(),
            expiry_date=timezone.now().date() + timedelta(days=365 * 3),
            cert_body=self.cert_body,
            scope="Existing certification scope",
        )

        self.client.force_login(self.admin_user)

        # Create a request object and mock the issue_certificate method to raise ValueError
        url = reverse("certification_bodies:issue_certificate", args=[self.completed_audit.pk])
        today = timezone.now().date()
        data = {
            "certificate_number": "DUPLICATE-NUMBER",  # This will cause a conflict
            "scope": "Test scope",
            "expiry_date": (today + timedelta(days=365 * 3)).strftime("%Y-%m-%d"),
        }

        # Temporarily modify the issue_certificate method to raise ValueError
        original_method = AuditResult.issue_certificate

        def mock_issue_certificate(*args, **kwargs):
            raise ValueError("Certificate number already exists")

        AuditResult.issue_certificate = mock_issue_certificate

        try:
            response = self.client.post(url, data)

            # Should stay on the form with error message
            self.assertEqual(response.status_code, 200)
            messages = list(response.context["messages"])
            self.assertTrue(any("Certificate number already exists" in str(m) for m in messages))
        finally:
            # Restore original method
            AuditResult.issue_certificate = original_method

    def test_issue_certificate_with_default_expiry(self):
        """Test certificate issuance using default expiry date."""
        # Create approved audit result
        _audit_result = AuditResult.objects.create(
            audit=self.completed_audit,
            decision="approve",
            comments="Approved",
            decided_by=self.admin_cb_user,
        )

        self.client.force_login(self.admin_user)

        # Submit form without specifying expiry date
        url = reverse("certification_bodies:issue_certificate", args=[self.completed_audit.pk])
        data = {
            "certificate_number": "DEFAULT-EXPIRY-CERT",
            "scope": "Test scope with default expiry",
            # No expiry_date specified - should use default
        }
        response = self.client.post(url, data)

        # Should create certificate with default expiry (3 years)
        self.assertEqual(response.status_code, 302)

        cert = Certification.objects.get(certificate_number="DEFAULT-EXPIRY-CERT")
        expected_expiry = timezone.now().date() + timedelta(days=365 * 3)
        self.assertEqual(cert.expiry_date, expected_expiry)
