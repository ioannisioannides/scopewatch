"""
Serializers for the Organizations app.

This module defines the serializers used for converting Organization model instances
to and from JSON format for the REST API.
"""

from rest_framework import serializers

from .models import Certification, Organization


class CertificationSerializer(serializers.ModelSerializer):
    """Serializer for Certification model."""

    class Meta:
        model = Certification
        fields = [
            "id",
            "certificate_number",
            "issue_date",
            "expiry_date",
            "organization",
            "cert_body",
        ]
        read_only_fields = ["id"]


class OrganizationSerializer(serializers.ModelSerializer):
    """Serializer for Organization model."""

    certifications = CertificationSerializer(many=True, read_only=True)

    class Meta:
        model = Organization
        fields = ["id", "name", "contact_email", "is_active", "certifications"]
        read_only_fields = ["id"]


class OrganizationDetailSerializer(OrganizationSerializer):
    """Detailed serializer for Organization model with additional fields."""

    class Meta(OrganizationSerializer.Meta):
        # Include all fields from the parent serializer
        pass
