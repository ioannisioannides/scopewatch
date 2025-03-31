# apps/audits/models.py

"""
Models for the Audits app.

This module defines the database models for the Audits app, including the Audit model,
which represents audit records linking organizations and certification bodies.
"""

from django.db import models
from apps.organizations.models import Organization
from apps.certification_bodies.models import CertBody

class Audit(models.Model):
    """
    Represents an audit record, linking organizations and certification bodies.

    Attributes:
        audit_type (str): The type of the audit (e.g., Stage1, Stage2).
        start_date (date): The start date of the audit.
        end_date (date): The end date of the audit.
        status (str): The current status of the audit.
        organization (ForeignKey): The organization being audited.
        certbody (ForeignKey): The certification body conducting the audit.
        created_at (datetime): The timestamp when the audit was created.
        updated_at (datetime): The timestamp when the audit was last updated.
    """
    audit_type = models.CharField(max_length=100)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=50, default='Scheduled')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='audits')
    certbody = models.ForeignKey(CertBody, on_delete=models.CASCADE, related_name='audits')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """
        Returns a string representation of the audit.

        Returns:
            str: A string containing the audit type and status.
        """
        return f"{self.audit_type} - {self.status}"
