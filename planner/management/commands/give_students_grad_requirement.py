#!/usr/bin/python

from django.core.management.base import BaseCommand, CommandError
from planner.models import Requirement, Student

class Command(BaseCommand):
    help = 'Makes sure every student has a graduation requirement'
    def handle(self, *args, **kwargs):
        foundational_core = Requirement.objects.get(name='Foundational Core')
        for s in Student.objects.all():
            Requirement.make_graduation_requirement(s)
                                  
            
