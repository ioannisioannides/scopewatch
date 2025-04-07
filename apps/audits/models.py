# apps/audits/models.py

"""
Models for the Audits app.

This module defines the database models for the Audits app.
"""

from typing import Type

from django.db import models

from apps.certification_bodies.models import CertBody, Auditor
from apps.organizations.models import Organization


class Audit(models.Model):
    """
    Represents an audit record in the system.

    Attributes:
        audit_type (str): The type of the audit (e.g., Stage1, Stage2).
        start_date (date): The start date of the audit.
        end_date (date): The end date of the audit.
        status (str): The current status of the audit.
        organization (ForeignKey): The organization being audited.
        certbody (ForeignKey): The certification body conducting the audit.
    """
    AUDIT_TYPE_CHOICES = [
        ('pre_assessment', 'Pre-Assessment'),
        ('stage1', 'Stage 1'),
        ('stage2', 'Stage 2'),
        ('surveillance', 'Surveillance'),
        ('recertification', 'Re-certification'),
    ]
    
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('closed', 'Closed'),
    ]

    audit_type = models.CharField(max_length=100, choices=AUDIT_TYPE_CHOICES)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="Scheduled")
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="audits"
    )
    certbody = models.ForeignKey(
        CertBody, on_delete=models.CASCADE, related_name="audits"
    )
    standard = models.CharField(max_length=255, help_text="The standard being audited against", default="ISO 9001:2015")
    notes = models.TextField(blank=True)

    objects: Type[models.Manager] = models.Manager()  # Add type hint for objects manager

    def __str__(self):
        return f"{self.get_audit_type_display()} - {self.organization.name} ({self.get_status_display()})"


class AuditTeam(models.Model):
    """
    Represents a team of auditors assigned to an audit.
    
    This model supports the business requirement that auditors can work alone or
    as part of an audit team.
    
    Attributes:
        audit (ForeignKey): The audit the team is assigned to.
        lead_auditor (ForeignKey): The lead auditor for this audit team.
    """
    audit = models.OneToOneField(Audit, on_delete=models.CASCADE, related_name="audit_team")
    lead_auditor = models.ForeignKey(
        Auditor, 
        on_delete=models.PROTECT, 
        related_name="lead_audits"
    )
    
    def __str__(self):
        return f"Audit Team for {self.audit}"


class AuditorAssignment(models.Model):
    """
    Represents the assignment of an auditor to an audit team.
    
    Attributes:
        team (ForeignKey): The audit team the auditor is assigned to.
        auditor (ForeignKey): The auditor assigned.
        role (str): The role of the auditor in this team.
        is_active (bool): Whether this assignment is active.
    """
    ROLE_CHOICES = [
        ('lead', 'Lead Auditor'),
        ('technical', 'Technical Expert'),
        ('trainee', 'Trainee Auditor'),
        ('observer', 'Observer'),
    ]
    
    team = models.ForeignKey(AuditTeam, on_delete=models.CASCADE, related_name="assignments")
    auditor = models.ForeignKey(Auditor, on_delete=models.CASCADE, related_name="assignments")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    assigned_date = models.DateField(auto_now_add=True)
    unassigned_date = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.auditor} - {self.team.audit} ({self.get_role_display()})"


class NonConformance(models.Model):
    """
    Represents a nonconformance found during an audit.
    
    Attributes:
        audit (ForeignKey): The audit in which the nonconformance was found.
        severity (str): The severity level of the nonconformance.
        description (str): Description of the nonconformance.
        date_raised (date): When the nonconformance was raised.
        date_closed (date): When the nonconformance was closed.
        requires_evidence (bool): Whether evidence is required to close this nonconformance.
    """
    SEVERITY_CHOICES = [
        ('major', 'Major'),
        ('minor', 'Minor'),
        ('observation', 'Observation'),
    ]
    
    audit = models.ForeignKey(Audit, on_delete=models.CASCADE, related_name='nonconformances')
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    description = models.TextField()
    date_raised = models.DateField(auto_now_add=True)
    date_closed = models.DateField(null=True, blank=True)
    requires_evidence = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.get_severity_display()} NC - {self.audit}"
