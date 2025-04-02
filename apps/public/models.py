# apps/public/models.py

"""
Models for the Public app.

This module defines models for the Public app. If you plan to store data specifically
for the public app, such as public certificate access logs, you can define models here.
"""

from django.db import models  # Keeping this import for potential future use

# Example model for tracking public certificate access logs:
#
# class CertificateAccessLog(models.Model):
#     """
#     Represents a log entry for public access to a certificate.
#
#     Attributes:
#         user (ForeignKey): The user who accessed the certificate.
#         certificate (ForeignKey): The certificate that was accessed.
#         accessed_at (DateTime): The timestamp of the access.
#         reason (TextField): The reason for accessing the certificate.
#     """
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
#     certificate = models.ForeignKey('certificates.Certificate', on_delete=models.CASCADE)
#     accessed_at = models.DateTimeField(auto_now_add=True)
#     reason = models.TextField(blank=True)
#
#     def __str__(self):
#         return f"Certificate Access by {self.user} on {self.accessed_at}"
