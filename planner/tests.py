from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse

class HomePageTest(TestCase):
    def test_home_page(self):
        client = Client()
        response = client.get('/')
        self.assertContains(response, 'iGrad Four Year Planner')

class LoginTest(TestCase):
    def setUp(self):
        self.client = Client()

class PlannerTest(TestCase):
    def test_login(self):
        """
        Test basic login.
        """
        login = self.client.login(username='majorStudent', password='password')

