# apps/consultants/models.py

"""
Models for the Consultants app.

This module defines the database models for consultants and consultancy firms.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.apps import apps

from apps.organizations.models import Organization

# Use get_user_model() instead of directly importing User
User = get_user_model()


class ConsultancyFirm(models.Model):
    """
    Represents a consultancy firm that prepares organizations for certification.
    
    Attributes:
        name (str): The name of the consultancy firm.
        address (str): The physical address of the consultancy firm.
        website (str): The website of the consultancy firm.
        specialties (str): Areas of specialty for the consultancy firm.
        is_active (bool): Whether the consultancy firm is active.
    """
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255, blank=True)
    contact_email = models.EmailField(null=True, blank=True)
    website = models.URLField(blank=True)
    specialties = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name


class Consultant(models.Model):
    """
    Represents an individual consultant who prepares organizations for certification.
    
    Attributes:
        user (OneToOneField): The user account for this consultant.
        firm (ForeignKey): The consultancy firm this consultant works for.
        bio (str): Biographical information about the consultant.
        specialties (str): The consultant's areas of specialty.
        specialty (str): The primary specialty of the consultant (for backward compatibility).
        standards (str): The standards the consultant is familiar with.
        is_active (bool): Whether the consultant is active.
        is_independent (bool): Whether the consultant works independently.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    firm = models.ForeignKey(
        ConsultancyFirm, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='consultants'
    )
    bio = models.TextField(blank=True)
    specialties = models.CharField(max_length=255, blank=True)
    specialty = models.CharField(max_length=255, blank=True)  # For backward compatibility
    standards = models.CharField(max_length=255, blank=True)
    experience_years = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_independent = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.user.get_full_name() or self.user.username


class ConsultantEngagement(models.Model):
    """
    Represents an engagement between a consultant and an organization.
    
    This model supports the business requirement that consultants prepare 
    organizations for certification.
    
    Attributes:
        consultant (ForeignKey): The consultant engaged.
        organization (ForeignKey): The organization being consulted for.
        start_date (date): When the engagement started.
        end_date (date): When the engagement ended (if applicable).
        standards (str): The standards the consultant is helping with.
        status (str): The current status of the engagement.
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
        ('cancelled', 'Cancelled'),
    ]
    
    consultant = models.ForeignKey(Consultant, on_delete=models.CASCADE, related_name='engagements')
    organization = models.ForeignKey(
        Organization, 
        on_delete=models.CASCADE, 
        related_name='consultant_engagements'
    )
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True)
    standards = models.CharField(max_length=255, default='ISO 9001')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.consultant} - {self.organization} ({self.get_status_display()})"


class ConsultantDocument(models.Model):
    """
    Represents a document prepared by a consultant for an organization.
    
    This model supports the business requirement of tracking documentation 
    prepared by consultants to help organizations become certified.
    
    Attributes:
        consultant (ForeignKey): The consultant who prepared the document.
        organization (ForeignKey): The organization the document is for.
        engagement (ForeignKey): The consultant engagement this document belongs to.
        title (str): The title of the document.
        document_type (str): The type of document.
        standard (str): The standard this document is prepared for.
        status (str): The current status of the document.
        file (FileField): The actual document file.
    """
    DOCUMENT_TYPES = [
        ('policy', 'Policy Document'),
        ('procedure', 'Procedure'),
        ('work_instruction', 'Work Instruction'),
        ('form', 'Form Template'),
        ('record', 'Record'),
        ('manual', 'Manual'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('review', 'Under Review'),
        ('approved', 'Approved by Organization'),
        ('submitted', 'Submitted to Audit'),
        ('rejected', 'Rejected'),
        ('archived', 'Archived'),
    ]
    
    consultant = models.ForeignKey(Consultant, on_delete=models.CASCADE, related_name='documents')
    organization = models.ForeignKey(
        Organization, 
        on_delete=models.CASCADE, 
        related_name='consultant_documents'
    )
    engagement = models.ForeignKey(
        ConsultantEngagement,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    title = models.CharField(max_length=255)
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    standard = models.CharField(
        max_length=255,
        help_text="The standard this document is prepared for"
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    file = models.FileField(upload_to='consultant_documents/')
    notes = models.TextField(blank=True)
    # Use the string reference to break circular dependency
    submitted_to_audit = models.ForeignKey(
        'audits.Audit',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='submitted_consultant_documents'
    )
    
    def __str__(self):
        return f"{self.title} - {self.organization.name}"
    
    def submit_to_audit(self, audit):
        """
        Submits this document to an audit.
        
        Args:
            audit (Audit): The audit to submit the document to
        
        Returns:
            DocumentSubmission: The newly created document submission
        """
        # Use get_model to break circular dependency
        DocumentSubmission = apps.get_model('audits', 'DocumentSubmission')
        
        # Update this document's status
        self.status = 'submitted'
        self.submitted_to_audit = audit
        self.save()
        
        # Check if document type matches any in DocumentSubmission types
        doc_types = [c[0] for c in DocumentSubmission.DOCUMENT_TYPES]
        final_doc_type = self.document_type if self.document_type in doc_types else 'other'
        
        # Create a DocumentSubmission
        submission = DocumentSubmission.objects.create(
            audit=audit,
            title=self.title,
            document_type=final_doc_type,
            submitted_by=self.consultant.user,
            consultant=self.consultant,
            file=self.file,
            notes=f"Submitted from consultant document: {self.title}"
        )
        
        return submission
