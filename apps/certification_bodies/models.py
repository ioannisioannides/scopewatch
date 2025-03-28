# apps/certification_bodies/models.py

from django.db import models

class CertBody(models.Model):
    """
    Represents a Certification Body, which can conduct audits and issue certificates.
    """
    name = models.CharField(max_length=255)
    accreditation_id = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True)
    contact_email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
