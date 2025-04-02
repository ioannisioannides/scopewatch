# apps/consultants/models.py

"""
Models for the Consultants app.

This module defines the database models for the Consultants app, including the Consultant and ConsultancyFirm models,
which represent individual consultants and consultancy firms, respectively.
"""

from django.conf import settings
from django.db import models


class Consultant(models.Model):
    """
    Represents an individual consultant who can assist organizations with compliance preparations.

    Attributes:
        user (ForeignKey): The user associated with the consultant.
        specialty (str): The specialty or area of expertise of the consultant.
        is_active (bool): Indicates whether the consultant is active.
        created_at (datetime): The timestamp when the consultant was created.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='consultant_profile'
    )
    specialty = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.specialty}"

class ConsultancyFirm(models.Model):
    """
    Represents a firm that employs multiple consultants.

    Attributes:
        name (str): The name of the consultancy firm.
        address (str): The address of the consultancy firm.
        contact_email (str): The contact email of the consultancy firm.
        is_active (bool): Indicates whether the consultancy firm is active.
        created_at (datetime): The timestamp when the consultancy firm was created.
    """
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True)
    contact_email = models.EmailField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
