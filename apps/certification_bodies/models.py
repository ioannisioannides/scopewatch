# apps/certification_bodies/models.py

"""
Models for the Certification Bodies app.

This module defines the database models for the Certification Bodies app, 
including the CertBody model.
The CertBody model represents certification bodies that conduct audits and issue certificates.
"""

from django.db import models

class CertBody(models.Model):
    """
    Represents a Certification Body, which can conduct audits and issue certificates.

    Attributes:
        name (str): The name of the certification body.
        accreditation_id (str): The accreditation ID of the certification body.
        address (str): The address of the certification body.
        contact_email (str): The contact email of the certification body.
        created_at (datetime): The timestamp when the certification body was created.
        is_active (bool): Indicates whether the certification body is active.
    """
    name = models.CharField(max_length=255)
    accreditation_id = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True)
    contact_email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        """
        Returns a string representation of the certification body.

        Returns:
            str: The name of the certification body.
        """
        return self.name
