# apps/consultants/tests.py

"""
Unit tests for the Consultants app.

This module contains test cases for the Consultant and ConsultancyFirm models.
These tests ensure that the models behave as expected when creating and validating instances.
"""

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from .models import ConsultancyFirm, Consultant, ConsultantEngagement
from apps.organizations.models import Organization


class ConsultantsModelTest(TestCase):
    """
    Test suite for the Consultant and ConsultancyFirm models.
    """

    def test_create_consultant(self):
        """
        Test the creation of a Consultant instance.
        """
        user = User.objects.create_user(
            username="consultant_user", password="password"
        )  # Ensure user is created with a password
        consultant = Consultant.objects.create(
            user=user, specialty="ISO 9001", is_active=True
        )
        self.assertEqual(consultant.user.username, "consultant_user")
        self.assertEqual(consultant.specialty, "ISO 9001")
        self.assertTrue(consultant.is_active)
        self.assertFalse(consultant.is_independent)

    def test_create_independent_consultant(self):
        """
        Test the creation of an independent Consultant instance.
        """
        user = User.objects.create_user(
            username="independent_consultant", password="password"
        )
        consultant = Consultant.objects.create(
            user=user,
            specialty="ISO 27001",
            is_active=True,
            is_independent=True
        )
        self.assertEqual(consultant.user.username, "independent_consultant")
        self.assertEqual(consultant.specialty, "ISO 27001")
        self.assertTrue(consultant.is_active)
        self.assertTrue(consultant.is_independent)
        self.assertIsNone(consultant.firm)

    def test_create_consultancy_firm(self):
        """
        Test the creation of a ConsultancyFirm instance.
        """
        firm = ConsultancyFirm.objects.create(
            name="Global Consulting", 
            contact_email="contact@globalconsulting.com",
            address="123 Consulting Ave, Business District"
        )
        self.assertEqual(firm.name, "Global Consulting")
        self.assertEqual(firm.contact_email, "contact@globalconsulting.com")
        self.assertEqual(firm.address, "123 Consulting Ave, Business District")
        self.assertTrue(firm.is_active)
        self.assertIsNotNone(firm.created_at)


class ConsultantViewTest(TestCase):
    """
    Test suite for the Consultant views.
    """

    def setUp(self):
        """
        Set up test data for the Consultant views.
        """
        self.user = User.objects.create_user(username="consultant_user")
        self.consultant = Consultant.objects.create(
            user=self.user, specialty="ISO 9001"
        )
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
        self.organization = Organization.objects.create(name="Client Organization", contact_email="client@example.com")
        self.consultant = Consultant.objects.create(user=self.user, specialty="ISO 9001", is_independent=True)
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
            engagement_type='project',
            description="Implementation of ISO 9001 quality management system"
        )
        
        self.assertEqual(engagement.consultant, self.consultant)
        self.assertEqual(engagement.organization, self.organization)
        self.assertEqual(engagement.engagement_type, 'project')
        self.assertTrue(engagement.is_active)
        self.assertEqual(engagement.end_date, self.today + timedelta(days=30))
    
    def test_long_term_engagement(self):
        """
        Test creating a long-term support engagement.
        """
        engagement = ConsultantEngagement.objects.create(
            consultant=self.consultant,
            organization=self.organization,
            start_date=self.today,
            engagement_type='long_term',
            description="Ongoing quality management system maintenance"
        )
        
        self.assertEqual(engagement.consultant, self.consultant)
        self.assertEqual(engagement.organization, self.organization)
        self.assertEqual(engagement.engagement_type, 'long_term')
        self.assertTrue(engagement.is_active)
        self.assertIsNone(engagement.end_date)
