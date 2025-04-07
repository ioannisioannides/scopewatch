# apps/certification_bodies/models.py

"""
Models for the Certification Bodies app.

This module defines the database models for the Certification Bodies app.
"""

from django.db import models


class CertBody(models.Model):
    """
    Represents a certification body in the system.

    Attributes:
        name (str): The name of the certification body.
        accreditation_id (str): The accreditation ID of the certification body.
        address (str): The address of the certification body.
        created_at (datetime): The timestamp when the certification body was created.
    """
    name = models.CharField(max_length=255)
    accreditation_id = models.CharField(max_length=100)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Returns a string representation of the certification body.

        Returns:
            str: The name of the certification body.
        """
        return str(self.name)  # Ensure the return value is a string
