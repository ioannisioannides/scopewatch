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


class ConsultantDocument(models.Model):
    """
    Represents a document prepared by a consultant for an organization.
    
    This model supports the business requirement that consultants help organizations
    prepare documentation for certification bodies to issue certificates.
    
    Attributes:
        consultant (ForeignKey): The consultant who prepared the document.
        organization (ForeignKey): The organization the document is prepared for.
        title (str): The title of the document.
        document_type (str): The type of document.
        standard (str): The standard the document is related to.
        engagement (ForeignKey): The consultant engagement this document is part of.
        created_at (datetime): When the document was created.
        updated_at (datetime): When the document was last updated.
        status (str): The current status of the document.
        file (FileField): The actual document file.
        submitted_to_audit (ForeignKey): The audit this document was submitted to (if any).
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
    
    consultant = models.ForeignKey(
        'Consultant',
        on_delete=models.CASCADE,
        related_name='documents'
    )
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='consultant_documents'
    )
    title = models.CharField(max_length=255)
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    standard = models.CharField(max_length=255, help_text="The standard this document is prepared for")
    engagement = models.ForeignKey(
        'ConsultantEngagement',
        on_delete=models.CASCADE,
        related_name='documents'
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    file = models.FileField(upload_to='consultant_documents/')
    submitted_to_audit = models.ForeignKey(
        'audits.Audit',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='submitted_consultant_documents'
    )
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.title} ({self.get_document_type_display()})"
    
    def submit_to_audit(self, audit):
        """
        Submit this document to a specific audit.
        
        Args:
            audit: The audit to submit this document to
            
        Returns:
            The created DocumentSubmission object
        """
        from apps.audits.models import DocumentSubmission
        
        if self.status != 'approved':
            raise ValueError("Only approved documents can be submitted to an audit")
        
        # Create a DocumentSubmission
        submission = DocumentSubmission.objects.create(
            audit=audit,
            title=self.title,
            document_type='other',  # Default mapping
            submitted_by=self.consultant.user,
            consultant=self.consultant,
            file=self.file
        )
        
        # Update this document
        self.submitted_to_audit = audit
        self.status = 'submitted'
        self.save()
        
        return submission
