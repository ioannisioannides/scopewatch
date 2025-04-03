# apps/consultants/models.py

"""
Models for the Consultants app.

This module defines the database models for the Consultants app.
"""

from django.conf import settings
from django.db import models


class Consultant(models.Model):
    """
    Represents a consultant in the system.

    Attributes:
        user (ForeignKey): The user associated with the consultant.
        specialty (str): The specialty of the consultant.
        is_active (bool): Indicates whether the consultant is active.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="consultant_profile"
    )
    specialty = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        """
        Returns a string representation of the consultant.

        Returns:
            str: The username of the consultant's user.
        """
        return self.user.username


class ConsultancyFirm(models.Model):
    """
    Represents a consultancy firm in the system.

    Attributes:
        name (str): The name of the consultancy firm.
        address (str): The address of the consultancy firm.
        contact_email (str): The contact email of the consultancy firm.
        is_active (bool): Indicates whether the consultancy firm is active.
    """

    name = models.CharField(max_length=255)
    address = models.TextField(blank=True)
    contact_email = models.EmailField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        """
        Returns a string representation of the consultancy firm.

        Returns:
            str: The name of the consultancy firm.
        """
        return self.name
