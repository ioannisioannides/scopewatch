# apps/audits/models.py

from django.db import models

class Audit(models.Model):
    """
    Represents an audit record, linking organizations and certification bodies.
    Add fields like audit_type, start_date, end_date, status, etc.
    """
    audit_type = models.CharField(max_length=100)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=50, default='Scheduled')

    # Example foreign key placeholders (uncomment or adjust as needed):
    # organization = models.ForeignKey(
    #     'organizations.Organization', on_delete=models.CASCADE, related_name='audits'
    # )
    # certbody = models.ForeignKey(
    #     'certification_bodies.CertBody', on_delete=models.CASCADE, related_name='audits'
    # )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.audit_type} - {self.status}"
