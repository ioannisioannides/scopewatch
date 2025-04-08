# apps/public/models.py

"""
Models for the Public app.

This module defines the database models for the Public app, which handles
public-facing features like certificate verification.
"""

from django.db import models
from django.utils import timezone


class CertificationVerification(models.Model):
    """
    Tracks public verification requests for certificates.
    
    This model helps track and monitor how often certificates are being verified
    and by whom (anonymously).
    
    Attributes:
        certificate (ForeignKey): The certificate that was verified.
        verification_date (datetime): When the verification occurred.
        ip_address (str): The IP address of the verifier (anonymized).
        user_agent (str): The user agent of the verifier.
    """
    certificate = models.ForeignKey(
        'organizations.Certification',
        on_delete=models.CASCADE,
        related_name='verification_records'
    )
    verification_date = models.DateTimeField(default=timezone.now)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    
    def __str__(self):
        return f"Verification of {self.certificate} on {self.verification_date}"


class SearchLog(models.Model):
    """
    Tracks certificate search queries from the public.
    
    This model helps analyze what the public is searching for and improve
    the search functionality.
    
    Attributes:
        search_term (str): What was searched for.
        search_date (datetime): When the search occurred.
        results_count (int): Number of results returned.
        ip_address (str): The IP address of the searcher (anonymized).
    """
    search_term = models.CharField(max_length=255)
    search_date = models.DateTimeField(default=timezone.now)
    results_count = models.IntegerField(default=0)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    
    def __str__(self):
        return f"Search for '{self.search_term}' ({self.results_count} results)"
