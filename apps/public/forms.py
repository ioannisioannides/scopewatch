# apps/public/forms.py

"""
Forms for the Public app.

This module provides forms for public users to search for certifications.
"""

from django import forms
from apps.organizations.models import Certification
from apps.certification_bodies.models import CertBody


class CertificateSearchForm(forms.Form):
    """
    Form for searching certifications.
    """

    search_term = forms.CharField(
        label="Search",
        max_length=255,
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Search by organization name, certificate number, or scope",
                "class": "form-control",
            }
        ),
    )

    standard = forms.ChoiceField(
        label="Standard",
        required=False,
        choices=[("", "-- Any Standard --")],
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    certification_body = forms.ChoiceField(
        label="Certification Body",
        required=False,
        choices=[("", "-- Any Certification Body --")],
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Get all distinct standards for the dropdown
        standards = (
            Certification.objects.values_list("standard", flat=True)
            .distinct()
            .order_by("standard")
        )
        self.fields["standard"].choices += [(std, std) for std in standards]

        # Get all active certification bodies for the dropdown
        cert_bodies = (
            CertBody.objects.filter(is_active=True)
            .values_list("id", "name")
            .order_by("name")
        )
        self.fields["certification_body"].choices += [
            (cb_id, name) for cb_id, name in cert_bodies
        ]


class CertificationVerificationForm(forms.Form):
    """
    Form for verifying certification by certificate number.
    """
    
    certificate_number = forms.CharField(
        label="Certificate Number",
        max_length=255,
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Enter certificate number",
                "class": "form-control",
            }
        ),
    )
