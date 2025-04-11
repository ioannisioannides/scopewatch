# apps/audits/models.py

"""
Models for the Audits app.

This module defines the database models for the Audits app.
"""

from typing import Type

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

# Use string references instead of direct imports to avoid circular dependencies
# from apps.certification_bodies.models import CertBody, Auditor, CertBodyUser
# from apps.organizations.models import Organization, Certification
# from apps.consultants.models import Consultant

# Get the User model
User = get_user_model()


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
        scheduled_date (date): When the audit is scheduled to take place.
    """

    AUDIT_TYPE_CHOICES = [
        ("pre_assessment", "Pre-Assessment"),
        ("stage1", "Stage 1"),
        ("stage2", "Stage 2"),
        ("surveillance", "Surveillance"),
        ("recertification", "Re-certification"),
    ]

    STATUS_CHOICES = [
        ("scheduled", "Scheduled"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("closed", "Closed"),
        ("certification_issued", "Certification Issued"),
    ]

    audit_type = models.CharField(max_length=100, choices=AUDIT_TYPE_CHOICES)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    scheduled_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=50, choices=STATUS_CHOICES, default="scheduled"
    )
    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.CASCADE, related_name="audits"
    )
    certbody = models.ForeignKey(
        "certification_bodies.CertBody", on_delete=models.CASCADE, related_name="audits"
    )
    standard = models.CharField(
        max_length=255,
        help_text="The standard being audited against",
        default="ISO 9001:2015",
    )
    notes = models.TextField(blank=True)

    objects: Type[models.Manager] = (
        models.Manager()
    )  # Add type hint for objects manager

    def __str__(self):
        return (
            f"{self.get_audit_type_display()} - {self.organization.name} "
            f"({self.get_status_display()})"
        )

    def issue_certification(self, scope, certificate_number, issue_date, expiry_date):
        """
        Issues a new certification based on this audit.

        Args:
            scope: The scope of the certification
            certificate_number: The unique certificate number
            issue_date: The date the certificate is issued
            expiry_date: The expiration date of the certificate

        Returns:
            The newly created Certification object

        Raises:
            ValueError: If the audit status doesn't allow certification
            ValueError: If the certificate dates are invalid
            ValueError: If the certificate number is already in use
        """
        from apps.organizations.models import Certification

        # Check if a certification already exists for this audit
        try:
            if hasattr(self, "resulting_certification"):
                return self.resulting_certification
        except Certification.DoesNotExist:
            pass

        # Validate audit status
        if self.status not in ["completed", "closed"]:
            raise ValueError(
                f"Cannot issue certification for an audit with status: {self.get_status_display()}. "
                "Audit must be 'Completed' or 'Closed'."
            )

        # Validate dates
        today = timezone.now().date()
        if issue_date > today:
            raise ValueError("Certificate issue date cannot be in the future")

        if expiry_date <= issue_date:
            raise ValueError("Certificate expiry date must be after the issue date")

        # Validate certificate number uniqueness
        if Certification.objects.filter(certificate_number=certificate_number).exists():
            raise ValueError(
                f"Certificate number '{certificate_number}' is already in use"
            )

        # Create a new certification
        certification = Certification.objects.create(
            organization=self.organization,
            cert_body=self.certbody,
            standard=self.standard,
            certificate_number=certificate_number,
            issue_date=issue_date,
            expiry_date=expiry_date,
            scope=scope,
            audit=self,
        )

        # Update the audit status
        self.status = "certification_issued"
        self.save()

        return certification


class AuditTeam(models.Model):
    """
    Represents a team of auditors assigned to an audit.

    This model supports the business requirement that auditors can work alone or
    as part of an audit team.

    Attributes:
        audit (ForeignKey): The audit the team is assigned to.
        lead_auditor (ForeignKey): The lead auditor for this audit team.
    """

    audit = models.OneToOneField(
        Audit, on_delete=models.CASCADE, related_name="audit_team"
    )
    lead_auditor = models.ForeignKey(
        "certification_bodies.Auditor",
        on_delete=models.PROTECT,
        related_name="lead_audits",
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
        ("lead", "Lead Auditor"),
        ("technical", "Technical Expert"),
        ("trainee", "Trainee Auditor"),
        ("observer", "Observer"),
    ]

    team = models.ForeignKey(
        AuditTeam, on_delete=models.CASCADE, related_name="assignments"
    )
    auditor = models.ForeignKey(
        "certification_bodies.Auditor",
        on_delete=models.CASCADE,
        related_name="assignments",
    )
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
        ("major", "Major"),
        ("minor", "Minor"),
        ("observation", "Observation"),
    ]

    audit = models.ForeignKey(
        Audit, on_delete=models.CASCADE, related_name="nonconformances"
    )
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    description = models.TextField()
    date_raised = models.DateField(auto_now_add=True)
    date_closed = models.DateField(null=True, blank=True)
    requires_evidence = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.get_severity_display()} NC - {self.audit}"


class DocumentSubmission(models.Model):
    """
    Represents a document submitted for an audit.

    This model tracks documentation submitted by consultants and organizations
    for the certification process.

    Attributes:
        audit (ForeignKey): The audit this document is submitted for.
        title (str): The title or name of the document.
        document_type (str): The type of document.
        submitted_by (ForeignKey): The user who submitted the document.
        submitted_at (datetime): When the document was submitted.
        consultant (ForeignKey): The consultant who prepared this document (optional).
        status (str): The current status of the document review.
        notes (str): Additional notes about the document.
        file (FileField): The actual document file.
    """

    DOCUMENT_TYPES = [
        ("policy", "Policy Document"),
        ("procedure", "Procedure"),
        ("record", "Record"),
        ("evidence", "Compliance Evidence"),
        ("report", "Report"),
        ("other", "Other"),
    ]

    STATUS_CHOICES = [
        ("submitted", "Submitted"),
        ("under_review", "Under Review"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("needs_revision", "Needs Revision"),
    ]

    audit = models.ForeignKey(Audit, on_delete=models.CASCADE, related_name="documents")
    title = models.CharField(max_length=255)
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    submitted_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="submitted_documents"
    )
    submitted_at = models.DateTimeField(default=timezone.now)
    consultant = models.ForeignKey(
        "consultants.Consultant",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="prepared_documents",
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="submitted"
    )
    notes = models.TextField(blank=True)
    file = models.FileField(upload_to="audit_documents/")

    def __str__(self):
        return f"{self.title} - {self.audit}"


class AuditResult(models.Model):
    """
    Represents the formal result of an audit.

    This model supports the business requirement that audits lead to certification
    decisions by providing a formal outcome of the audit process.

    Attributes:
        audit (OneToOneField): The audit this result belongs to.
        decision (str): The certification decision (approve, conditional, reject).
        decision_date (date): When the decision was made.
        decided_by (ForeignKey): The certification body user who made the decision.
        comments (TextField): Additional notes about the decision.
        nonconformances_closed (bool): Whether all nonconformances are closed.
        recommendation (str): The auditor's recommendation.
    """

    DECISION_CHOICES = [
        ("approve", "Approve Certification"),
        ("conditional", "Conditional Approval"),
        ("reject", "Reject Certification"),
        ("followup", "Followup Audit Required"),
    ]

    RECOMMENDATION_CHOICES = [
        ("issue", "Issue Certificate"),
        ("withhold", "Withhold Certificate"),
        ("withdraw", "Withdraw Certificate"),
        ("followup", "Followup Required"),
    ]

    audit = models.OneToOneField(Audit, on_delete=models.CASCADE, related_name="result")
    decision = models.CharField(max_length=20, choices=DECISION_CHOICES)
    decision_date = models.DateField(default=timezone.now)
    decided_by = models.ForeignKey(
        "certification_bodies.CertBodyUser",
        on_delete=models.PROTECT,
        related_name="audit_decisions",
    )
    comments = models.TextField(blank=True)
    nonconformances_closed = models.BooleanField(default=False)
    recommendation = models.CharField(
        max_length=20, choices=RECOMMENDATION_CHOICES, blank=True
    )

    def __str__(self):
        return f"Result for {self.audit}: {self.get_decision_display()}"

    def can_issue_certificate(self):
        """
        Checks if a certificate can be issued based on this audit result.

        Returns:
            bool: True if a certificate can be issued, False otherwise.
        """
        return self.decision in ["approve", "conditional"] and (
            self.nonconformances_closed or self.decision == "approve"
        )

    def issue_certificate(self, certificate_number, scope, expiry_date):
        """
        Issues a certificate based on this audit result.

        Args:
            certificate_number (str): The certificate number to use
            scope (str): The scope of certification
            expiry_date (date): The expiration date of the certificate

        Returns:
            Certification: The newly created certification
        """
        if not self.can_issue_certificate():
            raise ValueError("Cannot issue certificate with current audit result")

        return self.audit.issue_certification(
            scope=scope,
            certificate_number=certificate_number,
            issue_date=timezone.now().date(),
            expiry_date=expiry_date,
        )
