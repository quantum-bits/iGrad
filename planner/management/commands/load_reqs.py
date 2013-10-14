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
        self.NAME = req.NAME 
        self.COURSES = req.COURSES
        self.EXCEPT = req.EXCEPT 
        for spec in req.requirements:
            name = spec[self.NAME]
            requirement,created = Requirement.objects.get_or_create(name = name, display_name = name)
            if created: print 'Created new requirement: ' + name
            else: print name + ': Requirement already created.'
            self.handle_courses(requirement, spec)

    def addCourse(self, subject, number, req):
        try:
            c = Course.objects.get(subject__abbrev=subject, number=number)
            req.courses.add(c)
            print 'Successfully added {} {} to {}'.format(subject, number, req)
        except Course.DoesNotExist:
            print 'Tried adding {} {} to {}. Course not found.'.format(subject, number, req)

    def addCourseRange(self, subject, min_number, max_number, req):
        for number in range(min_number, max_number + 1):
            self.addCourse(subject, number, req)

    def addCoursePattern(self, subject, req, exceptions=None):
        if exceptions:
            print 'Adding courses in {} subject. Except: {}'.format(subject, 
                                                                    ','.join(map(str,exceptions)))
        else:
            print 'Adding courses in {} subject.'

        exception_numbers = [e.split()[1] for e in exceptions]
        numbers = [c.number for c in Course.objects.filter(subject__abbrev=subject)
                   if c.number not in exception_numbers]
        for n in numbers:
            self.addCourse(subject, n, req)

    def handle_courses(self, requirement, spec):
        for c in spec.get(self.COURSES, []):
            match = re.match(r'^[A-Z]{3,4} \d{3}$', c)
            if match is not None:
                subject, number = match.group().split()
                self.addCourse(subject, int(number), requirement)
                
            match = re.match(r'^[A-Z]{3-4} \d{3}\-\d{3}$', c)
            if match is not None:
                subject, number_range = match.group().split()
                min_number, max_number = [int(i) for i in number_range.split('-')]
                self.addCourseRange(subject, min_number, max_number, requirement)

            match = re.match(r'^[A-Z]{3,4} \d{3}/\d{3}', c)
            if match is not None:
                subject, numbers = match.group().split()
                for number in numbers.split('/'): 
                    self.addCourse(subject, int(number), requirement)

            match = re.match(r'^[A-Z]{3,4}\*$', c)
            if match is not None:
                subject = match.group()[:-1]
                self.addCoursePattern(subject, requirement, spec.get(self.EXCEPT, []))


