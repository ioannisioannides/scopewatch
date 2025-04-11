# apps/consultants/tests.py

"""
Tests for the consultants app.

This module contains tests for models, views, and forms related to
consultants and consultancy firms.
"""

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()

from apps.consultants.models import ConsultancyFirm, Consultant, ConsultantEngagement
from apps.organizations.models import Organization
from apps.utils.test_credentials import get_test_credential


class ConsultantModelTest(TestCase):
    """
    Test cases for Consultant model
    """

    def test_create_consultant_with_firm(self):
        """
        Test creating a consultant associated with a consultancy firm.
        """
        user = User.objects.create_user(
            username=get_test_credential("consultant", "username"),
            password=get_test_credential("consultant", "password"),
        )  # Ensure user is created with a password
        consultant = Consultant.objects.create(
            user=user,
            bio="Experienced consultant with over 10 years in the field.",
            specialties="ISO 27001, ISO 9001",
            is_active=True,
        )

        # Create a consultancy firm and associate the consultant
        firm = ConsultancyFirm.objects.create(
            name="Quality Consultants Inc.",
            address="123 Consulting Ave, Suite 200",
            contact_email="contact@qualityconsultants.com",
            is_active=True,
        )
        consultant.firm = firm
        consultant.save()

        self.assertEqual(consultant.user, user)
        self.assertEqual(consultant.firm, firm)
        self.assertIn("ISO 27001", consultant.specialties)
        self.assertTrue(consultant.is_active)

    def test_create_independent_consultant(self):
        """
        Test creating an independent consultant (not associated with a firm).
        """
        user = User.objects.create_user(
            username=get_test_credential("consultant", "username", "independent_consultant"),
            password=get_test_credential("consultant", "password"),
        )
        consultant = Consultant.objects.create(
            user=user,
            bio="Independent consultant with expertise in ISO standards.",
            specialties="ISO 14001, ISO 45001",
            is_active=True,
        )

        self.assertEqual(consultant.user, user)
        self.assertIsNone(consultant.firm)
        self.assertIn("ISO 14001", consultant.specialties)
        self.assertTrue(consultant.is_active)


class ConsultantViewTest(TestCase):
    """
    Test suite for the Consultant views.
    """

    def setUp(self):
        """
        Set up test data for the Consultant views.
        """
        self.user = User.objects.create_user(username="consultant_user")
        self.consultant = Consultant.objects.create(user=self.user, specialty="ISO 9001")
        self.firm = ConsultancyFirm.objects.create(name="Test Firm")

    def test_consultant_list_view(self):
        """
        Test the consultant list view.
        """
        response = self.client.get(reverse("consultant_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ISO 9001")

    def test_consultancy_firm_list_view(self):
        """
        Test the consultancy firm list view.
        """
        response = self.client.get(reverse("consultancy_firm_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Firm")


class ConsultantEngagementTest(TestCase):
    """
    Test suite for consultant engagements.
    """

    def setUp(self):
        self.user = User.objects.create_user(username="engagement_consultant")
        self.organization = Organization.objects.create(
            name="Client Organization", contact_email="client@example.com"
        )
        self.consultant = Consultant.objects.create(
            user=self.user, specialty="ISO 9001", is_independent=True
        )
        self.today = timezone.now().date()

    def test_project_engagement(self):
        """
        Test creating a project-based engagement.
        """
        engagement = ConsultantEngagement.objects.create(
            consultant=self.consultant,
            organization=self.organization,
            start_date=self.today,
            end_date=self.today + timedelta(days=30),
            standards="ISO 9001",
            status="active",
            notes="Implementation of ISO 9001 quality management system",
        )

        self.assertEqual(engagement.consultant, self.consultant)
        self.assertEqual(engagement.organization, self.organization)
        self.assertEqual(engagement.status, "active")
        self.assertEqual(engagement.end_date, self.today + timedelta(days=30))

    def test_long_term_engagement(self):
        """
        Test creating a long-term support engagement.
        """
        engagement = ConsultantEngagement.objects.create(
            consultant=self.consultant,
            organization=self.organization,
            start_date=self.today,
            standards="ISO 9001",
            status="active",
            notes="Ongoing quality management system maintenance",
        )

        self.assertEqual(engagement.consultant, self.consultant)
        self.assertEqual(engagement.organization, self.organization)
        self.assertEqual(engagement.status, "active")
        self.assertIsNone(engagement.end_date)
