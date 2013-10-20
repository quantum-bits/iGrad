from django.core.management.base import BaseCommand, CommandError
from planner.models import Course, Requirement, Constraint
import re
import importlib
import os
import sys
import itertools

def addCourse(subject, number, req):
    try:
        c = Course.objects.get(subject__abbrev=subject, number=number)
        req.courses.add(c)
        print 'Successfully added {} {} to {}'.format(subject, number, req)
    except Course.DoesNotExist:
        print 'Tried adding {} {} to {}. Course not found.'.format(subject, number, req)

def addConstraint(fn):
    """Decorator that takes the constraint_text returned by a fn 
    and tries to add the corresponding constraint to the requirement.
    If it can't find it, creates one and adds to the requirement."""
    def inner(self, req, spec, match):
        constraint_text  = fn(self, req, spec, match)
        try:
            constraint = Constraint.objects.get(constraint_text=constraint_text)
        except Constraint.DoesNotExist:
            constraint = Constraint(name=constraint_text,
                                    constraint_text=constraint_text)
            constraint.save()
        req.constraints.add(constraint)
        print 'Added {} to {}'.format(constraint, req)
    return inner

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        sys.path.insert(0, 'planner/requirements')
        req_file = args[0]
        req = importlib.import_module(req_file)
        self.NAME = req.NAME 
        self.COURSES = req.COURSES
        self.EXCEPT = req.EXCEPT 
        self.CONSTRAINTS = req.CONSTRAINTS
        self.REQS = req.REQS
        self.handle_requirements(req.requirements)
        
    def handle_requirements(self, requirements, parent=None):
        for spec in requirements:
            name = spec[self.NAME]
            requirement,created = Requirement.objects.get_or_create(name = name, display_name = name)
            if created:
                print 'Created new requirement: ' + name
            else:
                print name + ': Requirement already created.'
            if parent is not None:
                parent.requirements.add(requirement)
                print 'Added {} to {} requirements.'.format(requirement, parent)
            self.handle_courses(requirement, spec, self.COURSES)
            self.handle_constraints(requirement, spec, self.CONSTRAINTS)
            self.handle_requirements(spec.get(self.REQS, []), requirement)

                
    def addCourse(self, req, spec, match):
        item = match.group()
        subject, number = item.split()
        addCourse(subject, int(number), req)
        
    def addCourseList(self, req, spec, match):
        item = match.group()
        "Add comma separated course list to req."
        subject, numbers = item.split()
        for n in numbers.split(','): addCourse(subject, n, req)
        
    def addCourseRange(self, req, spec, match):
        item = match.group()
        subject, number_range = item.split()
        min_number, max_number = [int(i) for i in number_range.split('-')]
        courses = Course.objects.filter(subject__abbrev=subject)
        courses = courses.filter(number__gte=min_number)
        courses = courses.filter(number__lte=max_number)
        req.courses.add(*courses)
        print 'Added: {}'.format('\n'.join(str(c) for c in courses))


    def addCourseAlternative(self, req, spec, match):
        item = match.group()
        subject, alternatives = item.split()
        for number in alternatives.split('/'): addCourse(subject, number, req)

    def addCoursePattern(self, req,spec,match):
        item = match.group()
        exceptions = spec.get(self.EXCEPT, [])
        subject = item[:-1]
        if exceptions:
            print 'Adding courses in {} subject. Except: {}'.format(subject, 
                                                                    ','.join(map(str,exceptions)))
        else:
            print 'Adding courses in {} subject.'

        exception_numbers = [e.split()[1] for e in exceptions]
        numbers = (c.number for c in Course.objects.filter(subject__abbrev=subject)
                   if c.number not in exception_numbers)
        for n in numbers: addCourse(subject, n, req)
    
    @addConstraint
    def addAllConstraint(self, req, spec, match):
        return 'all'

    @addConstraint
    def addNCourseConstraint(self, req, spec, match):
        n = match.group('n')
        return 'meet_some_at_least {}'.format(n)

    @addConstraint
    def addCourseCreditsConstraint(self, req, spec, match):
        n = match.group('n')
        return 'min_required_credit_hours at_least {} all False'.format(n)

    @addConstraint
    def addAllReqConstraint(self, req, spec, match):
        return 'all_sub_requirements_satisfied'

    @addConstraint
    def addReqNConstraint(self, req, spec, match):
        n = match.group('n')
        return 'satisfy_some_sub_requirements at_least {}'.format(n)

    @addConstraint
    def addReqCreditsConstraint(self, req, spec, match):
        n = match.group('n')
        return 'min_required_credit_hours at_least {} all True'.format(n)
    
    def spec_handler(re_dict):
        """Takes a dictionary that maps mutually-exclusive reg-exes
        to a method. Will pass the matching string to the method."""
        def __inner(self, requirement, spec, key):
            for item, re in itertools.product(spec.get(key, []), re_dict):
                match =  re.match(item)
                if match is not None:
                    re_dict[re](self,requirement, spec, match)
        return __inner

    handle_courses = spec_handler({
            re.compile(r'^[A-Z]{3,4} \d{3}$')            :addCourse,
            re.compile(r'^[A-Z]{3,4} \d{3}\-\d{3}$')     :addCourseRange,
            re.compile(r'^[A-Z]{3,4} \d{3}\/\d{3}$')     :addCourseAlternative,
            re.compile(r'^[A-Z]{3,4} \d{3}(?:,\d{3})+$') :addCourseList,
            re.compile(r'^[A-Z]{3,4}\*$')                :addCoursePattern
            }
    )

    handle_constraints = spec_handler({
            re.compile(r'^course_all$')                   :addAllConstraint,
            re.compile(r'^courses_n\((?P<n>\d+)\)$')      :addNCourseConstraint,
            re.compile(r'^course_credits\((?P<n>\d+)\)$') :addCourseCreditsConstraint,
            re.compile(r'^req_all$')                      :addAllReqConstraint,
            re.compile(r'^req_n\((?P<n>\d+)\)$')          :addReqNConstraint,
            re.compile(r'^req_credits\((?P<n>\d+)\)$')    :addReqCreditsConstraint,
            }
    )



