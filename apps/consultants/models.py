# apps/consultants/models.py

"""
Models for the Consultants app.

This module defines the database models for the Consultants app, including
Consultant and ConsultancyFirm, which represent individuals and firms
helping organizations comply with standards or regulations.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


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
    created_at = models.DateTimeField(default=timezone.now)  # Changed from auto_now_add to default

    objects = models.Manager()  # Add type hint for objects manager

    def __str__(self):
        return str(self.name)  # Ensure it returns a string


class Consultant(models.Model):
    """
    Represents a consultant in the system.

    A consultant can either work independently or be affiliated with a consultancy firm.

    Attributes:
        user (User): The user associated with this consultant profile.
        specialty (str): The consultant's area of expertise.
        firm (ConsultancyFirm): The consultancy firm the consultant belongs to (optional).
        is_active (bool): Whether the consultant is currently active.
        is_independent (bool): Whether the consultant works independently.
    """
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="consultant_profile"
    )
    specialty = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    firm = models.ForeignKey(
        ConsultancyFirm, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name="consultants"
    )
    is_independent = models.BooleanField(default=False)

    # Ensure the objects manager is explicitly defined
    objects = models.Manager()

    def __str__(self):
        """
        Returns a string representation of the consultant.

        Returns:
            str: The username of the consultant's user, or 'Unknown User' if not available.
        """
        return str(self.user.username) if hasattr(self.user, 'username') else 'Unknown User'


class ConsultantEngagement(models.Model):
    """
    Represents an engagement between a consultant and an organization.

    This model supports the business requirement that consultants help organizations
    prepare documentation for certification bodies.

    Attributes:
        consultant (Consultant): The consultant providing services.
        organization (Organization): The organization receiving consulting services.
        start_date (date): When the engagement started.
        end_date (date): When the engagement is scheduled to end (can be null for ongoing).
        is_active (bool): Whether the engagement is currently active.
        engagement_type (str): The type of engagement (project-based or long-term).
        description (str): Description of the consulting work.
    """
    ENGAGEMENT_TYPES = [
        ('project', 'Project Based'),
        ('long_term', 'Long Term Support'),
    ]
    
    consultant = models.ForeignKey(
        Consultant, 
        on_delete=models.CASCADE,
        related_name="engagements"
    )
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name="consultant_engagements"
    )
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    engagement_type = models.CharField(max_length=20, choices=ENGAGEMENT_TYPES)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.consultant} - {self.organization} ({self.get_engagement_type_display()})"
