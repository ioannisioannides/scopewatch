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
        return self.name


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
    cert_body = models.ForeignKey(
        CertBody, on_delete=models.CASCADE, related_name="users"
    )
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
        return self.user.get_full_name() or self.user.username

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

    auditor = models.ForeignKey(
        Auditor, on_delete=models.CASCADE, related_name="qualifications"
    )
    standard = models.CharField(max_length=255)
    cert_body = models.ForeignKey(
        CertBody, on_delete=models.CASCADE, related_name="verified_qualifications"
    )
    qualification_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)
    evidence_document = models.FileField(
        upload_to="auditor_qualifications/", null=True, blank=True
    )
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
