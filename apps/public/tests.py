# apps/public/tests.py

from django.test import TestCase
from django.urls import reverse


class PublicAppTest(TestCase):
    """
    Basic placeholder test class for the Public app.
    """

    def test_placeholder(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)


class PublicViewTest(TestCase):
    """
    Test suite for the Public views.
    """

    def test_home_view(self):
        """
        Test the home view.

        This test ensures that the home view returns a 200 status code
        and contains the expected content.
        """
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Welcome to Scopewatch")
