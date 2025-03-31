# apps/organizations/models.py

"""
Models for the Organizations app.

This module defines the database models for the Organizations app, including the Organization model,
which represents organizations that may request certifications or be audited.
"""

from django.db import models

class Organization(models.Model):
    """
    Represents an organization that may request certifications or be audited.

    Attributes:
        name (str): The name of the organization.
        address (str): The address of the organization.
        contact_email (str): The contact email of the organization.
        contact_phone (str): The contact phone number of the organization.
        created_at (datetime): The timestamp when the organization was created.
        is_active (bool): Indicates whether the organization is active.
    """
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True)
    contact_email = models.EmailField(blank=True, null=True)
    contact_phone = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
