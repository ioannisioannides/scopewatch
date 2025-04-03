# apps/organizations/models.py

"""
Models for the Organizations app.

This module defines the database models for the Organizations app.
"""

from django.db import models


class Organization(models.Model):
    """
    Represents an organization in the system.

    Attributes:
        name (str): The name of the organization.
        contact_email (str): The contact email of the organization.
    """

    name = models.CharField(max_length=255)
    contact_email = models.EmailField()

    def __str__(self):
        """
        Returns a string representation of the organization.

        Returns:
            str: The name of the organization.
        """
        return self.name
