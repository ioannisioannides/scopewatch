# apps/organizations/models.py

"""
Models for the Organizations app.

This module defines the database models for the Organizations app.
"""

from typing import Type

from django.db import models
from apps.certification_bodies.models import CertBody


class Organization(models.Model):
    """
    Represents an organization in the system.

    Attributes:
        name (str): The name of the organization.
        contact_email (str): The contact email of the organization.
    """

    name = models.CharField(max_length=255)
    contact_email = models.EmailField()

    objects: Type[models.Manager] = models.Manager()  # Add type hint for objects manager

    def __str__(self):
        """
        Returns a string representation of the organization.

        Returns:
            str: The name of the organization.
        """
        return str(self.name)  # Ensure the return value is a string


class Certification(models.Model):
    """
    Represents a certification issued to an organization.

    Attributes:
        organization (ForeignKey): The organization that received the certification.
        cert_body (ForeignKey): The certification body that issued the certification.
        certificate_number (str): The unique certificate number.
        issue_date (date): The date the certification was issued.
        expiry_date (date): The date the certification expires.
    """

    organization = models.ForeignKey(
        "Organization", on_delete=models.CASCADE, related_name="certifications"
    )
    cert_body = models.ForeignKey(
        CertBody, on_delete=models.CASCADE, related_name="certifications"
    )
    certificate_number = models.CharField(max_length=100, unique=True)
    issue_date = models.DateField()
    expiry_date = models.DateField()

    def __str__(self):
        """
        Returns a string representation of the certification.

        Returns:
            str: The certificate number.
        """
        return self.certificate_number
