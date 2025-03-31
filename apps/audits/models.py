# apps/audits/models.py

from django.db import models
from apps.organizations.models import Organization
from apps.certification_bodies.models import CertBody

class Audit(models.Model):
    """
    Represents an audit record, linking organizations and certification bodies.
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
        return f"{self.audit_type} - {self.status}"
