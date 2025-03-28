# apps/consultants/tests.py

from django.test import TestCase
from django.contrib.auth.models import User
from .models import Consultant, ConsultancyFirm

class ConsultantsModelTest(TestCase):

    def test_create_consultant(self):
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
        firm = ConsultancyFirm.objects.create(name="Global Consulting")
        self.assertEqual(firm.name, "Global Consulting")
        self.assertTrue(firm.is_active)
