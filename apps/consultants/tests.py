# apps/consultants/tests.py

"""
Unit tests for the Consultants app.

This module contains test cases for the Consultant and ConsultancyFirm models.
These tests ensure that the models behave as expected when creating and validating instances.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from .models import Consultant, ConsultancyFirm

class ConsultantsModelTest(TestCase):
    """
    Test suite for the Consultant and ConsultancyFirm models.

    This class contains unit tests for creating and validating instances
    of the Consultant and ConsultancyFirm models.
    """

    def test_create_consultant(self):
        """
        Test the creation of a Consultant instance.

        This test ensures that a Consultant instance can be created with valid data
        and that its attributes are correctly set.
        """
        user = User.objects.create_user(username='consultant_user')
        consultant = Consultant.objects.create(
            user=user,
            specialty="ISO 9001",
            is_active=True
        )
        self.assertEqual(consultant.user.username, 'consultant_user')
        self.assertEqual(consultant.specialty, "ISO 9001")
        self.assertTrue(consultant.is_active)

    def test_create_consultancy_firm(self):
        """
        Test the creation of a ConsultancyFirm instance.

        This test ensures that a ConsultancyFirm instance can be created with valid data
        and that its attributes are correctly set.
        """
        firm = ConsultancyFirm.objects.create(name="Global Consulting")
        self.assertEqual(firm.name, "Global Consulting")
        self.assertTrue(firm.is_active)
