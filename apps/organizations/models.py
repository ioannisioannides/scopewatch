# apps/organizations/models.py

"""
Models for the Organizations app.

This module defines the database models for organizations and their certifications.
"""

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

# Use string reference instead of direct import to avoid circular dependencies
# from apps.certification_bodies.models import CertBody

# Use get_user_model() instead of directly importing User
User = get_user_model()


class Organization(models.Model):
    """
    Represents an organization in the ScopeWatch system.

    Attributes:
        name (str): The name of the organization.
        address (str): The physical address of the organization.
        contact_email (str): The contact email for the organization.
        website (str): The website of the organization.
        is_active (bool): Whether the organization is currently active in the system.
        created_at (datetime): When the organization was first added.
        updated_at (datetime): When the organization was last updated.
        industry (str): The industry sector the organization operates in.
    """

    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255, blank=True)
    contact_email = models.EmailField()
    website = models.URLField(blank=True)
    industry = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)


class OrganizationUser(models.Model):
    """
    Represents a user associated with an organization.

    This model supports the business requirement that users can be associated
    with specific organizations with different roles.

    Attributes:
        user (OneToOneField): The user account for this organization user.
        organization (ForeignKey): The organization this user belongs to.
        role (str): The role of the user within the organization.
        is_active (bool): Whether the user is currently active for this organization.
    """

    ROLE_CHOICES = [
        ("admin", "Administrator"),
        ("manager", "Manager"),
        ("staff", "Staff"),
        ("viewer", "Viewer"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="users")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_username()} ({self.role}) at {self.organization.name}"


class Certification(models.Model):
    """
    Represents a certification held by an organization.

    Attributes:
        organization (ForeignKey): The organization holding the certification.
        cert_body (ForeignKey): The certification body that issued the certification.
        standard (str): The standard the organization is certified against.
        certificate_number (str): The unique certificate number.
        issue_date (date): The date the certification was issued.
        expiry_date (date): The date the certification expires.
        scope (TextField): The scope of certification activities covered.
        audit (OneToOneField): The audit that resulted in this certification.
        is_valid (bool): Whether the certification is currently valid.
    """

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="certifications"
    )
    # Temporarily removed to resolve migration issues
    # cert_body = models.ForeignKey(
    #     "certification_bodies.CertBody",
    #     on_delete=models.PROTECT,
    #     related_name="issued_certifications",
    # )
    standard = models.CharField(max_length=255)
    certificate_number = models.CharField(
        max_length=100, unique=True, help_text="The unique certificate identifier"
    )
    issue_date = models.DateField()
    expiry_date = models.DateField()
    scope = models.TextField(
        blank=True,
        help_text="The scope of certification - what activities, processes, or sites are covered.",
    )
    # Temporarily removed to resolve migration issues
    # audit = models.OneToOneField(
    #     "audits.Audit",
    #     on_delete=models.SET_NULL,
    #     null=True,
    #     blank=True,
    #     related_name="resulting_certification",
    # )

    def __str__(self):
        return f"{self.organization.name} - {self.standard} (#{self.certificate_number})"

    @property
    def is_valid(self):
        """
        Checks if the certification is currently valid.

        Returns:
            bool: True if valid, False if expired
        """
        return self.expiry_date >= timezone.now().date()

    def clean(self):
        """
        Validates certification dates.
        """
        if self.issue_date and self.expiry_date and self.expiry_date < self.issue_date:
            raise ValidationError("Expiry date cannot be before issue date.")

    class Meta:
        unique_together = ("organization", "standard", "issue_date")  # Removed `cert_body`
