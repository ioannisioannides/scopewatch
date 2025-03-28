# apps/public/models.py

from django.db import models

# If you plan to store data specifically for the public app, add models here.
# You might create a model tracking public certificate access logs, for example:
# 
# class CertificateAccessLog(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
#     certificate = models.ForeignKey('certificates.Certificate', on_delete=models.CASCADE)
#     accessed_at = models.DateTimeField(auto_now_add=True)
#     reason = models.TextField(blank=True)
#
#     def __str__(self):
#         return f"Certificate Access by {self.user} on {self.accessed_at}"
