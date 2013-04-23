"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase

class PlannerTest(TestCase):
    def test_login(self):
        """
        Test basic login.
        """
        login = self.client.login(username='majorStudent', password='password')
