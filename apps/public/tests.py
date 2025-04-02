# apps/public/tests.py

from django.test import TestCase
from django.urls import reverse


class PublicAppTest(TestCase):
    """
    Basic placeholder test class for the Public app.
    """
    def test_placeholder(self):
        self.assertTrue(True)

class PublicViewTest(TestCase):
    def test_home_view(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Welcome to Scopewatch")
