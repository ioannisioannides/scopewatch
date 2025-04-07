# apps/certification_bodies/models.py

"""
Models for the Certification Bodies app.

This module defines the database models for the Certification Bodies app.
"""

from django.db import models
from django.contrib.auth.models import User


class CertBody(models.Model):
    """
    Represents a certification body in the system.

    Attributes:
        name (str): The name of the certification body.
        accreditation_id (str): The accreditation ID of the certification body.
        address (str): The address of the certification body.
        contact_email (str): The contact email of the certification body.
        created_at (datetime): The timestamp when the certification body was created.
        is_active (bool): Whether the certification body is active.
    """
    name = models.CharField(max_length=255)
    accreditation_id = models.CharField(max_length=100)
    address = models.TextField(blank=True)
    contact_email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.name)  # Ensure it returns a string


class CertBodyUser(models.Model):
    """
    Represents a user associated with a certification body.

    This model supports the business requirement for certification bodies to have 
    multiple users to issue certificates, schedule audits, assign auditors, etc.

    Attributes:
        user (User): The user associated with the certification body.
        cert_body (CertBody): The certification body the user is associated with.
        role (str): The role of the user in the certification body.
        is_active (bool): Whether the user is currently active in this role.
        joined_date (date): The date when the user joined the certification body.
    """
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('auditor', 'Auditor'),
        ('secretary', 'Secretary'),
        ('accountant', 'Accountant'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cert_body_roles')
    cert_body = models.ForeignKey(CertBody, on_delete=models.CASCADE, related_name='staff')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    joined_date = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()} at {self.cert_body.name})"


class Auditor(models.Model):
    """
    Represents an auditor who can conduct audits.

    This model supports the business requirement that audits can only be conducted
    by auditors who are verified by certification bodies.

    Attributes:
        user (User): The user who is an auditor.
        cert_bodies (ManyToManyField): The certification bodies that have verified this auditor.
        specialties (str): The standards/frameworks the auditor is qualified to audit.
        is_active (bool): Whether the auditor is currently active.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='auditor_profile')
    cert_bodies = models.ManyToManyField(CertBody, related_name='verified_auditors')
    specialties = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Auditor: {self.user.username}"
