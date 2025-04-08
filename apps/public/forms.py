# apps/public/forms.py

"""
Forms for the Public app.

This module provides forms for public users to search for certifications.
"""

from django import forms
from apps.organizations.models import Certification


class CertificateSearchForm(forms.Form):
    """
    Form for searching certifications.
    """
    search_term = forms.CharField(
        label='Search',
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search by organization name, certificate number, or scope',
            'class': 'form-control'
        })
    )
    
    standard = forms.ChoiceField(
        label='Standard',
        required=False,
        choices=[('', '-- Any Standard --')],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Get all distinct standards for the dropdown
        standards = Certification.objects.values_list('standard', flat=True).distinct().order_by('standard')
        self.fields['standard'].choices += [(std, std) for std in standards]