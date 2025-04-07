# apps/audits/tests.py

"""
Unit tests for the Audits app.

This module contains test cases for the Audit model and its functionality.
Expand these tests to cover additional scenarios and edge cases.
"""

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from apps.audits.models import Audit, AuditTeam, AuditorAssignment, NonConformance
from apps.certification_bodies.models import CertBody, Auditor
from apps.organizations.models import Organization
from django.contrib.auth.models import User

import pytest
from django.test import Client


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
            audit_type="stage1",
            status="scheduled",
            organization=self.organization,
            certbody=self.cert_body,
            standard="ISO 9001:2015"
        )
        self.assertEqual(audit.audit_type, "stage1")
        self.assertEqual(audit.status, "scheduled")
        self.assertEqual(audit.organization.name, "Test Organization")
        self.assertEqual(audit.certbody.name, "Test Certification Body")
        self.assertEqual(audit.standard, "ISO 9001:2015")

    def test_audit_with_dates(self):
        """
        Test the creation of an Audit instance with start and end dates.
        """
        today = timezone.now().date()
        start_date = today + timedelta(days=10)
        end_date = today + timedelta(days=12)
        
        audit = Audit.objects.create(
            audit_type="stage2",
            status="scheduled",
            organization=self.organization,
            certbody=self.cert_body,
            standard="ISO 27001:2022",
            start_date=start_date,
            end_date=end_date
        )
        
        self.assertEqual(audit.start_date, start_date)
        self.assertEqual(audit.end_date, end_date)
        self.assertEqual(audit.audit_type, "stage2")

    def test_audit_status_update(self):
        """
        Test updating the status of an Audit instance.
        """
        audit = Audit.objects.create(
            audit_type="surveillance",
            status="scheduled",
            organization=self.organization,
            certbody=self.cert_body,
            standard="ISO 14001:2015"
        )
        
        # Update the status
        audit.status = "in_progress"
        audit.save()
        
        # Fetch the audit again
        updated_audit = Audit.objects.get(pk=audit.pk)
        self.assertEqual(updated_audit.status, "in_progress")


class AuditViewTest(TestCase):
    """
    Test suite for the Audit views.
    """

    def setUp(self):
        self.organization = Organization.objects.create(name="Test Org")
        self.cert_body = CertBody.objects.create(name="Test Cert Body")
        self.audit = Audit.objects.create(
            audit_type="stage1",
            status="scheduled",
            organization=self.organization,
            certbody=self.cert_body,
            standard="ISO 9001:2015"
        )

    def test_audit_list_view(self):
        """
        Test the audit list view.

        This test ensures that the audit list view returns a 200 status code
        and contains the expected audit data.
        """
        response = self.client.get(reverse("audit_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "stage1")

    def test_audit_detail_view(self):
        """
        Test the audit detail view.

        This test ensures that the audit detail view returns a 200 status code
        and contains the expected audit data.
        """
        response = self.client.get(reverse("audit_detail", args=[self.audit.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "stage1")


class AuditTeamTest(TestCase):
    """
    Test suite for the AuditTeam functionality.
    """
    
    def setUp(self):
        # Create organization and cert body
        self.organization = Organization.objects.create(
            name="Audited Organization", 
            contact_email="audit@example.com"
        )
        self.cert_body = CertBody.objects.create(
            name="Auditing Body", 
            accreditation_id="AB-123"
        )
        
        # Create auditor
        self.user = User.objects.create_user(username="lead_auditor")
        self.auditor = Auditor.objects.create(
            user=self.user, 
            specialties="ISO 9001, ISO 14001"
        )
        self.auditor.cert_bodies.add(self.cert_body)
        
        # Create audit
        self.audit = Audit.objects.create(
            audit_type="stage2",
            status="scheduled",
            organization=self.organization,
            certbody=self.cert_body,
            standard="ISO 9001:2015",
            start_date=timezone.now().date() + timedelta(days=5)
        )
    
    def test_audit_team_creation(self):
        """
        Test creating an audit team with lead auditor.
        """
        team = AuditTeam.objects.create(
            audit=self.audit,
            lead_auditor=self.auditor
        )
        
        self.assertEqual(team.audit, self.audit)
        self.assertEqual(team.lead_auditor, self.auditor)
        self.assertIn("Audit Team", str(team))
    
    def test_auditor_assignments(self):
        """
        Test auditor assignments to an audit team.
        """
        team = AuditTeam.objects.create(
            audit=self.audit,
            lead_auditor=self.auditor
        )
        
        # Create additional team members
        user2 = User.objects.create_user(username="technical_expert")
        technical_auditor = Auditor.objects.create(
            user=user2,
            specialties="Technical systems"
        )
        technical_auditor.cert_bodies.add(self.cert_body)
        
        user3 = User.objects.create_user(username="trainee_auditor")
        trainee_auditor = Auditor.objects.create(
            user=user3,
            specialties="In training"
        )
        trainee_auditor.cert_bodies.add(self.cert_body)
        
        # Assign auditors to team
        lead_assignment = AuditorAssignment.objects.create(
            team=team,
            auditor=self.auditor,
            role="lead"
        )
        
        tech_assignment = AuditorAssignment.objects.create(
            team=team,
            auditor=technical_auditor,
            role="technical"
        )
        
        trainee_assignment = AuditorAssignment.objects.create(
            team=team,
            auditor=trainee_auditor,
            role="trainee"
        )
        
        # Check assignments
        self.assertEqual(team.assignments.count(), 3)
        self.assertEqual(lead_assignment.role, "lead")
        self.assertEqual(tech_assignment.role, "technical")
        self.assertEqual(trainee_assignment.role, "trainee")


class NonConformanceTest(TestCase):
    """
    Test suite for the NonConformance model.
    """
    
    def setUp(self):
        # Create organization and cert body
        self.organization = Organization.objects.create(
            name="Audited Organization", 
            contact_email="audit@example.com"
        )
        self.cert_body = CertBody.objects.create(
            name="Auditing Body", 
            accreditation_id="AB-123"
        )
        
        # Create audit
        self.audit = Audit.objects.create(
            audit_type="stage2",
            status="in_progress",
            organization=self.organization,
            certbody=self.cert_body,
            standard="ISO 9001:2015"
        )
    
    def test_nonconformance_creation(self):
        """
        Test creating nonconformances with different severity levels.
        """
        major_nc = NonConformance.objects.create(
            audit=self.audit,
            severity="major",
            description="Critical failure in quality control process"
        )
        
        minor_nc = NonConformance.objects.create(
            audit=self.audit,
            severity="minor",
            description="Missing documentation for calibration records"
        )
        
        observation = NonConformance.objects.create(
            audit=self.audit,
            severity="observation",
            description="Consider improving labeling system"
        )
        
        self.assertEqual(major_nc.severity, "major")
        self.assertEqual(minor_nc.severity, "minor")
        self.assertEqual(observation.severity, "observation")
        self.assertTrue(major_nc.requires_evidence)
        self.assertTrue(minor_nc.requires_evidence)
        self.assertTrue(observation.requires_evidence)
    
    def test_nonconformance_closure(self):
        """
        Test closing a nonconformance.
        """
        nc = NonConformance.objects.create(
            audit=self.audit,
            severity="minor",
            description="Inadequate training records"
        )
        
        self.assertIsNone(nc.date_closed)
        
        # Close the nonconformance
        closure_date = timezone.now().date()
        nc.date_closed = closure_date
        nc.save()
        
        # Verify closure
        updated_nc = NonConformance.objects.get(pk=nc.pk)
        self.assertEqual(updated_nc.date_closed, closure_date)
