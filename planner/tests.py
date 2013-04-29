"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from planner.models import User

class PlannerTest(TestCase):

    #fixtures = ['test.json']

    def test_login(self):
        """
        Tests login of iGrad page
        1. Test to make sure unregistered user can't login
        2. Test that registered user can login
        """
        #Test Attributes of Login Page
        response = self.client.get('/accounts/login/?=next/')
        self.assertContains(response, 'iGrad Four Year Planner')
        self.assertContains(response, 'Login')
        self.assertContains(response, 'Not logged in.')


        #Unregistered user should not be able to login
        response = self.client.login(username="badUser",password="junk")
        self.assertFalse(response)

        #Registered user should be able to login
        response = self.client.login(username="majorStudent",password="foobar")
        self.assertTrue(response)
        self.assertContains(self.client.get('/'), 'Logged in as ')
        
        #A user is able to log out

