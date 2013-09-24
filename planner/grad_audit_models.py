#!/usr/bin/python
from collections import deque
from django.db import models
from models import CourseOffering
import itertools

class GradAudit(object):
    def __init__(self, **kwargs):
        self.requirement = kwargs.get('requirement')
        self.met_courses = kwargs.get('met_courses', {})
        self.is_satisfied = kwargs.get('is_satisfied')
        self.constraint_messages = kwargs.get('constraint_messages', [])
        self.children = kwargs.get('children', [])
        self.unused_courses = kwargs.get('unused_courses', None)
        self.unmet_prereqs = []
        self.unmet_coreqs = []
        self.student = kwargs.get('student', None)

    def addMessage(self, msg):
        self.constraint_messages.append(msg)

    def addChild(self, child):
        self.children.append(child)
        for met_course in child.met_courses:
            self.met_courses[met_course] = child.met_courses[met_course]

    def addChildren(self, *children):
        for child in children:
            self.addChild(child)

    def __iter__(self):
        self._stack = deque([])
        self._stack.append(self)
        return self
    
    def next(self):
        if not self._stack:
            raise StopIteration

        audit = self._stack.pop()
        for child in audit.children:
            self._stack.append(child)
        return audit


class GradAuditTemplate(object):
    def __init__(self, audit):
        self.audit = audit

    def semesterDescription(self, semester):
        yearName = self.audit.student.yearName(semester)
        semester_name = semester.name
        year = semester.begin_on.year
        return '{} {} ({})'.format(yearName, semester_name, year)

    def courseInfo(self, required_course):
        info = {}
        info['course_id'] = required_course.id
        info['title'] = required_course.title
        info['abbrev'] = required_course.abbrev
        info['credit_hours'] = required_course.possible_credit_hours
        info['sp'] = required_course.is_sp
        info['cc'] = required_course.is_cc
        if required_course in self.audit.met_courses:
            courseOffering = self.audit.met_courses[required_course]
            yearName = student.yearName(courseOffering.semester)
            semester_name = courseOffering.semester.name
            year = courseOffering.semester.begin_on.year
            info['met'] = True
            info['offering_id'] = courseOffering.id
            info['taken_for'] = courseOffering.credit_hours
            info['hours_match'] = courseOffering.credit_hours == required_course.credit_hours.min_credit_hour
            info['comment'] = self.semester_description(semester)
        else:
            info['comment'] = None
            info['met'] = False
        return info

    def requirementBlock(self, audit):
        """Creates requirement block information to be used directly
        in gradaudit.html template."""
        
        requirement = audit.requirement
        block = {}
        block['name'] = requirement.name
        block['min_required_credit_hours'] = requirement.min_required_credit_hours
        block['constraint_comments'] = audit.constraint_messages
        block['courses'] = []
        block['comments'] = []
        
        for course in requirement.required_courses():
            block['courses'].append(self.courseInfo(course))

        for prereq in audit.unmet_prereqs: pass
        for coreq in audit.unmet_coreqs: pass
        
        return block

    def requirementBlocks(self):
        """Returns requirementBlocks produced from each grad_audit."""
        return [self.requirementBlock(grad_audit) for grad_audit in self.audit]



class Constraint(models.Model):
    name = models.CharField(max_length = 80)
    constraint_text = models.CharField(max_length = 100)
    comment = models.CharField(max_length = 200, null=True, blank=True)

    def __unicode__(self):
        return self.name

    def parse_constraint_text(self):
        tokens = self.constraint_text.split()
        name,args = tokens[0],tokens[1:]
        parameters = {}
        for i in range(0, len(args), 2):
            parameters[args[i]] = args[i + 1]
        return (name, parameters)

    def remove_met_courses_from_unused_courses(self, met_courses, unused_courses):
        met_courses = met_courses.values()
        return unused_courses - set(met_courses)

    def audit(self, courseOfferings, requirement, unused_courses):
        name, arguments = self.parse_constraint_text()
        return getattr(self, name)(courseOfferings, requirement, unused_courses,**arguments)

    def any(self, courses, requirement, unused_courses, **kwargs):
        met_courses = requirement.met_courses(courses)
        unused_courses = self.remove_met_courses_from_unused_courses(met_courses, unused_courses)
        is_satisfied = len(met_courses) >= 1
        return GradAudit(requirement=requirement, is_satisfied=is_satisfied, met_courses=met_courses), unused_courses


    def all(self, courses, requirement, unused_courses, **kwargs):
        met_courses = requirement.met_courses(courses)
        unused_courses = self.remove_met_courses_from_unused_courses(met_courses, unused_courses)
        is_satisfied = len(met_courses) == len(requirement.required_courses())
        return GradAudit(requirement=requirement, is_satisfied=is_satisfied, met_courses=met_courses), unused_courses


    def meet_some(self, courses, requirement, unused_courses, **kwargs):
        at_least = int(kwargs['at_least'])
        met_courses = requirement.met_courses(courses)
        unused_courses = self.remove_met_courses_from_unused_courses(met_courses, unused_courses)        
        is_satisfied = len(met_courses) >= at_least
        return GradAudit(requirement=requirement, met_courses=met_courses, is_satisfied=is_satisfied), unused_courses
    

    def min_required_credit_hours (self, courses, requirement, unused_courses, **kwargs):
        at_least = int(kwargs['at_least'])
        course_offerings = [] 
        courses_considered = [] 
        met_courses = requirement.met_courses(courses, True)
        unused_courses = self.remove_met_courses_from_unused_courses(met_courses, unused_courses)
        def course_has_been_considered(course):
            return course in courses_considered

        for met_course in met_courses:
            course_offering = met_courses[met_course]
            course = course_offering.course
            if not course_has_been_considered(course):
                course_offerings.append(course_offering)
                courses_considered.append(course_offering.course)
        
        print ("\n".join(str(co) for co in course_offerings))
        is_satisfied = sum(co.credit_hours for co in course_offerings) >= at_least
        return GradAudit(requirement=requirement, is_satisfied=is_satisfied, met_courses=met_courses), unused_courses

    def different_departments(self, courses, requirement, unused_courses, **kwargs):
        at_least = int(kwargs['at_least'])
        met_courses = requirement.met_courses(courses, True)
        unused_courses = self.remove_met_courses_from_unused_courses(met_courses, unused_courses)
        courses = [met_course for met_course in met_courses]
        # TODO: Change this. The heuristic is that if a course has different abbreviations
        # it is from different departments. This is not always the case.
        unique_departments = set(course.subject.abbrev for course in courses)
        is_satisfied = len(unique_departments) >= at_least
        return GradAudit(requirement=requirement, met_courses=met_courses, is_satisfied=is_satisfied), unused_courses

    def sub_requirements_grad_audits(self, courses, requirement, unused_courses):
        """Returns a collection of grad audits, unused_courses."""
        grad_audits = []
        for child in requirement.child_requirements():
            grad_audit, unused_courses = child.audit(courses, unused_courses)
            grad_audits.append(grad_audit)
        return grad_audits, unused_courses 

    def all_sub_requirements_satisfied(self, courses, requirement, unused_courses, **kwargs):
        grad_audits, unused_courses = self.sub_requirements_grad_audits(courses, requirement, unused_courses)
        is_satisfied = all([grad_audit.is_satisfied for grad_audit in grad_audits])
        grad_audit = GradAudit(requirement=requirement, is_satisfied=is_satisfied, children=grad_audits)
        return grad_audit, unused_courses

    def satisfy_some_sub_requirements(self, courses, requirement, unused_courses, **kwargs):
        at_least = int(kwargs['at_least'])
        grad_audits, unused_courses = self.sub_requirements_grad_audits(courses, requirement, unused_courses)
        satisfied_grad_audits = [grad_audit for grad_audit in grad_audits if grad_audit.is_satisfied]
        is_satisfied = len(satisfied_grad_audits) >= at_least
        grad_audit = GradAudit(requirement=requirement, is_satisfied=is_satisfied, children=grad_audits)
        return grad_audit, unused_courses
    

class Requirement(models.Model):
    name = models.CharField(max_length=50,
                            help_text="e.g., PhysicsBS Technical Electives, or GenEd Literature;"
                            "first part is helpful for searching (when creating a major).")
    
    display_name = models.CharField(max_length=50,
                                    help_text="e.g., Technical Electives, or Literature;"
                                    "this is the title that will show up when students"
                                    "do a graduation audit.")

    min_required_credit_hours = models.PositiveIntegerField(default=0)
    constraints = models.ManyToManyField(Constraint, related_name='constraints', blank=True)
    requirements = models.ManyToManyField('self', symmetrical=False, blank=True, related_name = 'sub_requirements')
    courses = models.ManyToManyField('Course', related_name = 'courses', blank=True)

    def __unicode__(self):
        return self.name

    def required_courses(self):
        return list(self.courses.all())

    def all_courses(self):
        """ Returns the required from this requirement and any sub requirements."""
        reqs = self.requirements.all()
        req_courses = [list(req.all_courses()) for req in reqs]
        return self.required_courses() + (list(itertools.chain(*req_courses)))

    def audit(self, courses, unused_courses = None, **kwargs):
        """
        Returns a grad_audit, unused_courses
        """
        student = kwargs.get('student', None)
        def _inner(self, courses,unused_courses):
            """Examines a requirements constraints to create a grad_audit. 
            If all constraints are met, gradAudit is_satisfied. """
            
            grad_audit = GradAudit(requirement=self, student=student)

            is_satisfied = True
            for constraint in self.constraints.all():
                child_audit, unused_courses = constraint.audit(courses, self, unused_courses)
                is_satisfied = is_satisfied and child_audit.is_satisfied
                grad_audit.addMessage(constraint.name)
                if child_audit.requirement == self:
                    grad_audit.addChildren(*child_audit.children)
                else:
                    grad_audit.addChild(child_audit)
            return grad_audit, unused_courses

        if unused_courses is None: unused_courses = set(courses)
        return _inner(self, courses, unused_courses)


    def child_requirements(self):
        return self.requirements.all()

    def met_courses(self, courseOfferings, consider_all_courses=False):
        """ Returns a dictionary that maps a required_course to the course_offering/ substitute 
        that fulfills it. If all is true examines the courses from this requirement and sub_requirements.
        Otherwise only considers courses for this requirement.
        """
        offering_meets_course = lambda offering, course: offering.course == course

        if consider_all_courses:
            courses = self.all_courses()
        else:
            courses = self.required_courses()

        met_courses = {}
        for course in courses:
            for co in courseOfferings:
                if offering_meets_course(co, course):
                    met_courses[course] = co
        return met_courses
            
    class Meta:
        ordering = ['display_name', ]
