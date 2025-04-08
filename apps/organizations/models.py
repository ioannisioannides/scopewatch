# apps/organizations/models.py

"""
Models for the Organizations app.

This module defines the database models for the Organizations app.
"""

from typing import Type
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Organization(models.Model):
    """
    Represents an organization in the system.

    Attributes:
        name (str): The name of the organization.
        contact_email (str): The contact email of the organization.
        address (str): The address of the organization.
        is_active (bool): Indicates whether the organization is active.
        created_at (datetime): The timestamp when the organization was created.
    """

    name = models.CharField(max_length=255)
    contact_email = models.EmailField()
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)  # Changed from auto_now_add to default

    objects: Type[models.Manager] = models.Manager()  # Add type hint for objects manager

    def __str__(self):
        """
        Returns a string representation of the organization.

        Returns:
            str: The name of the organization.
        """
        return str(self.name)  # Ensure it returns a string


class OrganizationUser(models.Model):
    """
    Represents a user associated with an organization.

    This model supports the business requirement for organizations to have
    multiple users to communicate with certification bodies, consultants, etc.

    Attributes:
        user (User): The user associated with the organization.
        organization (Organization): The organization the user is associated with.
        role (str): The role of the user in the organization.
        is_active (bool): Whether the user is currently active in this role.
        joined_date (date): The date when the user joined the organization.
    """
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('editor', 'Editor'),
        ('viewer', 'Viewer'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organization_roles')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='staff')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    joined_date = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()} at {self.organization.name})"


class Certification(models.Model):
    """
    Represents a certification issued to an organization.

    Attributes:
        organization (ForeignKey): The organization that received the certification.
        cert_body (ForeignKey): The certification body that issued the certification.
        standard (CharField): The standard or framework the certification is for.
        certificate_number (str): The unique certificate number.
        issue_date (date): The date the certification was issued.
        expiry_date (date): The date the certification expires.
        scope (TextField): The scope of certification - what activities, processes, or sites are covered.
        audit (ForeignKey): The audit that resulted in this certification (can be null for legacy data).
    """
    organization = models.ForeignKey(
        "Organization", on_delete=models.CASCADE, related_name="certifications"
    )
    cert_body = models.ForeignKey(
        "certification_bodies.CertBody", on_delete=models.CASCADE, related_name="certifications"
    )
    standard = models.CharField(max_length=255, default="ISO 9001:2015")
    certificate_number = models.CharField(max_length=100, unique=True)
    issue_date = models.DateField()
    expiry_date = models.DateField()
    scope = models.TextField(blank=True, help_text="The scope of certification - what activities, processes, or sites are covered.")
    audit = models.OneToOneField(
        "audits.Audit", 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="resulting_certification"
    )

    def __str__(self):
        """
        Returns a string representation of the certification.

        Returns:
            str: The certificate number.
        """
        return str(self.certificate_number)  # Ensure it returns a string
    
    @property
    def is_valid(self):
        """
        Checks if the certification is currently valid based on its expiry date.
        
        Returns:
            bool: True if the certification is valid, False otherwise.
        """
        from django.utils import timezone
        
        return self.expiry_date >= timezone.now().date()
