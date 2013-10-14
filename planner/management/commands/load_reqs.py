from django.core.management.base import BaseCommand, CommandError
from planner.models import Course, Requirement

import re
import importlib
import os
import sys

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        sys.path.insert(0, 'planner/requirements')
        req_file = args[0]
        req = importlib.import_module(req_file)
        NAME, COURSES  = req.NAME, req.COURSES 
        for spec in req.requirements:
            name = spec[NAME]
            requirement,created = Requirement.objects.get_or_create(name = name, display_name = name)
            if created: print 'Created new requirement: ' + name
            else: print name + ': Requirement already created.'
            self.handle_courses(requirement, spec, COURSES)

    def addCourse(self, subject, number, req):
        try:
            c = Course.objects.get(subject__abbrev=subject, number=number)
            req.courses.add(c)
            print 'Successfully added {} {} to {}'.format(subject, number, req)
        except Course.DoesNotExist:
            print 'Tried adding {} {} to {}. Course not found.'.format(subject, number, req)

    def addCourses(self, subject, min_number, max_number, req):
        for number in range(min_number, max_number + 1):
            addCourse(subject, number, req)

    def handle_courses(self, requirement, spec, COURSES):
        for c in spec.get(COURSES, []):
            match = re.match(r'^[A-Z]{3,4} \d{3}$', c)
            if match is not None:
                subject, number = match.group().split()
                self.addCourse(subject, int(number), requirement)
            else:
                match = re.match(r'^[A-Z]{3-4} \d{3}\-\d{3}$', c)
                if match is not None:
                    subject, number_range = match.group.split()
                    min_number, max_number = [int(i) for i in number_range.split('-')]
                    self.addCourses(subject, min_number, max_number, requirement)                





