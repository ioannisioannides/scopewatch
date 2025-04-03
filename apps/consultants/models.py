# apps/consultants/models.py

"""
Models for the Consultants app.

This module defines the database models for the Consultants app, including
Consultant and ConsultancyFirm, which represent individuals and firms
helping organizations comply with standards or regulations.
"""

from typing import Type

from django.conf import settings
from django.db import models


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

    objects: Type[models.Manager] = models.Manager()  # Add type hint for objects manager

    def __str__(self):
        """
        Returns a string representation of the consultancy firm.

        Returns:
            str: The name of the consultancy firm.
        """
        return self.name


class Consultant(models.Model):
    """
    Represents a consultant in the system.

    Attributes:
        user (ForeignKey): The user associated with the consultant.
        specialty (str): The specialty of the consultant.
        firm (ForeignKey): The consultancy firm the consultant belongs to (optional).
        is_active (bool): Indicates whether the consultant is active.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="consultant_profile"
    )
    specialty = models.CharField(
        max_length=255,
        blank=True,
        help_text="The consultant's area of expertise."
    )
    firm = models.ForeignKey(
        ConsultancyFirm, on_delete=models.SET_NULL, null=True, blank=True, related_name="consultants"
    )
    is_active = models.BooleanField(default=True)

    objects: Type[models.Manager] = models.Manager()  # Add type hint for objects manager

    def __str__(self):
        """
        Returns a string representation of the consultant.

        Returns:
            str: The username of the consultant's user.
        """
        return str(self.user.username)  # Ensure the return value is a string
