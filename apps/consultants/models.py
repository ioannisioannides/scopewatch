# apps/consultants/models.py

from django.db import models
from django.conf import settings

class Consultant(models.Model):
    """
    Represents an individual consultant who can assist organizations
    with compliance preparations.
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
    """
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True)
    contact_email = models.EmailField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
