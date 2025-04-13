# apps/certification_bodies/models.py

"""
Models for the Certification Bodies app.

This module defines the database models for certification bodies and auditors.
"""

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

# Use get_user_model() instead of directly importing User
User = get_user_model()


class CertBody(models.Model):
    """
    Represents a certification body that issues certifications.

    Attributes:
        name (str): The name of the certification body.
        accreditation_id (str): The formal accreditation ID of the certification body.
        address (str): The physical address of the certification body.
        is_active (bool): Whether the certification body is active.
    """

    name = models.CharField(max_length=255)
    accreditation_id = models.CharField(max_length=100)
    address = models.CharField(max_length=255, blank=True)
    logo = models.ImageField(upload_to="certbody_logos/", null=True, blank=True)
    contact_email = models.EmailField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)


class CertBodyUser(models.Model):
    """
    Represents a user associated with a certification body.

    Attributes:
        user (OneToOneField): The user account for this certification body user.
        cert_body (ForeignKey): The certification body this user works for.
        role (str): The role of the user at the certification body.
    """

    ROLE_CHOICES = [
        ("admin", "Administrator"),
        ("manager", "Manager"),
        ("certifier", "Certification Manager"),
        ("staff", "Staff Member"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cert_body = models.ForeignKey(CertBody, on_delete=models.CASCADE, related_name="users")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} ({self.role}) at {self.cert_body.name}"


class Auditor(models.Model):
    """
    Represents an auditor at a certification body.

    Attributes:
        user (OneToOneField): The user account for this auditor.
        cert_bodies (ManyToManyField): The certification bodies this auditor works for.
        specialties (str): The specialties of the auditor.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cert_bodies = models.ManyToManyField(CertBody, related_name="auditors")
    specialties = models.CharField(max_length=255, blank=True)
    bio = models.TextField(blank=True)
    employee_id = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.user.get_full_name() or self.user.username)

    def can_audit_standard(self, standard, cert_body=None):
        """
        Checks if this auditor is qualified to audit a specific standard.

        Args:
            standard (str): The standard to check qualifications for
            cert_body (CertBody, optional): The certification body to check for.
                If None, checks across all certification bodies.

        Returns:
            bool: True if qualified, False otherwise
        """
        qualifications = self.qualifications.filter(standard=standard)

        if cert_body:
            qualifications = qualifications.filter(cert_body=cert_body)

        valid_qualifications = [q for q in qualifications if q.is_valid]

        return len(valid_qualifications) > 0


class StandardQualification(models.Model):
    """
    Represents an auditor's qualification for a specific standard.

    This model supports the business requirement of tracking
    auditor qualifications by standard.

    Attributes:
        auditor (ForeignKey): The auditor who holds this qualification.
        standard (str): The standard this qualification is for.
        cert_body (ForeignKey): The certification body that verifies this qualification.
        qualification_date (date): When the qualification was earned.
        expiry_date (date): When the qualification expires (if applicable).
        evidence_document (FileField): Supporting evidence for the qualification.
        notes (TextField): Additional information about the qualification.
    """

    auditor = models.ForeignKey(Auditor, on_delete=models.CASCADE, related_name="qualifications")
    standard = models.CharField(max_length=255)
    cert_body = models.ForeignKey(
        CertBody, on_delete=models.CASCADE, related_name="verified_qualifications"
    )
    qualification_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)
    evidence_document = models.FileField(upload_to="auditor_qualifications/", null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ("auditor", "standard", "cert_body")

    def __str__(self):
        return f"{self.auditor} - {self.standard} qualification"

    @property
    def is_valid(self):
        """
        Checks if the qualification is currently valid.

        Returns:
            bool: True if valid, False if expired
        """
        if not self.expiry_date:
            return True

        current_date = timezone.now().date()
        return self.expiry_date >= current_date

    @property
    def validity_status(self):
        """
        Returns a more detailed status about the qualification's validity.

        Returns:
            str: Status description ("valid", "expired", "expiring_soon")
        """
        if not self.expiry_date:
            return "valid"

        current_date = timezone.now().date()
        if self.expiry_date < current_date:
            return "expired"

        # Check if expiring within next 90 days
        expiring_soon_threshold = current_date + timezone.timedelta(days=90)
        if self.expiry_date <= expiring_soon_threshold:
            return "expiring_soon"

        return "valid"

    def clean(self):
        """
        Validates the qualification dates.
        """
        current_date = timezone.now().date()

        # Qualification date should not be in the future
        if self.qualification_date and self.qualification_date > current_date:
            raise ValidationError("Qualification date cannot be in the future")

        # Expiry date should be after qualification date
        if (
            self.expiry_date
            and self.qualification_date
            and self.expiry_date < self.qualification_date
        ):
            raise ValidationError("Expiry date cannot be before qualification date")

        # Standard should not be empty
        if not self.standard.strip():
            raise ValidationError("Standard cannot be empty")


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
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="scheduled")
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

    team = models.ForeignKey(AuditTeam, on_delete=models.CASCADE, related_name="assignments")
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

    audit = models.ForeignKey(Audit, on_delete=models.CASCADE, related_name="nonconformances")
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
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="submitted")
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
    recommendation = models.CharField(max_length=20, choices=RECOMMENDATION_CHOICES, blank=True)

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
