"""
API views for the Organizations app.

This module defines the API views for the Organizations app,
providing a RESTful interface for organization data.
"""

from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Certification, Organization
from .serializers import (
    CertificationSerializer,
    OrganizationDetailSerializer,
    OrganizationSerializer,
)


class OrganizationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows organizations to be viewed or edited.

    list:
    Return a list of all organizations.

    create:
    Create a new organization.

    retrieve:
    Return the given organization.

    update:
    Update the given organization.

    partial_update:
    Update parts of the given organization.

    destroy:
    Delete the given organization.
    """

    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        """Use different serializers for list and detail views."""
        if self.action == "retrieve":
            return OrganizationDetailSerializer
        return OrganizationSerializer

    @action(detail=True)
    def certifications(self, request, pk=None):
        """Return all certifications for the given organization."""
        organization = self.get_object()
        certifications = organization.certifications.all()
        serializer = CertificationSerializer(certifications, many=True)
        return Response(serializer.data)


class CertificationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows certifications to be viewed or edited.

    list:
    Return a list of all certifications.

    create:
    Create a new certification.

    retrieve:
    Return the given certification.

    update:
    Update the given certification.

    partial_update:
    Update parts of the given certification.

    destroy:
    Delete the given certification.
    """

    queryset = Certification.objects.all()
    serializer_class = CertificationSerializer
    permission_classes = [permissions.IsAuthenticated]
