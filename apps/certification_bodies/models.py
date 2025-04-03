# apps/certification_bodies/models.py

"""
Models for the Certification Bodies app.

This module defines the database models for the Certification Bodies app.
"""

from typing import Type

from django.db import models


class CertBody(models.Model):
    """
    Represents a certification body in the system.

    Attributes:
        name (str): The name of the certification body.
        accreditation_id (str): The accreditation ID of the certification body.
    """

    name = models.CharField(max_length=255)
    accreditation_id = models.CharField(max_length=100)

    objects: Type[models.Manager] = models.Manager()  # Add type hint for objects manager

    def __str__(self):
        """
        Returns a string representation of the certification body.

        Returns:
            str: The name of the certification body.
        """
        return str(self.name)  # Ensure the return value is a string
