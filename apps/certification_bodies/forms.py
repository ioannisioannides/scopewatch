# apps/certification_bodies/forms.py

from django import forms
from django.utils import timezone

from apps.audits.models import AuditResult
from apps.organizations.models import Certification


class AuditDecisionForm(forms.ModelForm):
    """
    Form for recording audit decisions.
    """
    class Meta:
        model = AuditResult
        fields = ['decision', 'nonconformances_closed', 'recommendation', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 4}),
        }


class CertificationIssueForm(forms.Form):
    """
    Form for issuing a certificate based on an audit result.
    """
    certificate_number = forms.CharField(
        max_length=100,
        label="Certificate Number",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    scope = forms.CharField(
        label="Certification Scope",
        widget=forms.Textarea(attrs={'rows': 4, 'class': 'form-control'})
    )
    expiry_date = forms.DateField(
        label="Expiry Date",
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'min': timezone.now().date().isoformat()
        }),
        help_text="If not specified, defaults to 3 years from today"
    )