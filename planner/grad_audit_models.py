#!/usr/bin/python
from django.db import models
import itertools
from collections import deque, namedtuple
from models import CourseOffering

RequirementBlock = namedtuple('RequirementBlock', ('name', 'constraints', 
                                                   'courses', 'min_required_credit_hours',))
class GradAudit(object):
    def __init__(self, **kwargs):
        self.requirement = kwargs.get('requirement')
        self.met_courses = kwargs.get('met_courses')
        self.is_satisfied = kwargs.get('is_satisfied')
        self.children = []

    def addChildren(self, *children):
        for child in children:
            self.children.append(child)

    def removeChildren(self, *children):
        for child in children:
            self.children.remove(child)
    
    def semester_description(self, student, courseOffering):
        yearName = student.yearName(courseOffering.semester)
        semester_name = courseOffering.semester.semester_name
        year = courseOffering.semester.begin_on.year
        return "{yearName} {semester_name} ({year})".format(yearName = yearName,
                                                            semester_name = semster_name, 
                                                            year = year)
    def make_course_info(self,student,required_course):
        info = {}
        info['course_id'] = required_course.id
        info['title'] = required_course.title
        info['abbrev'] = required_course.abbrev
        info['credit_hours'] = required_course.possible_credit_hours
        info['sp'] = required_course.is_sp
        info['cc'] = required_course.is_cc
        if required_course in self.met_courses:
            courseOffering = self.met_courses[required_course]
            yearName = student.yearName(courseOffering.semester)
            semester_name = courseOffering.semester.semester_name
            year = courseOffering.semester.begin_on.year
            info['offering_id'] = courseOffering.id
            info['taken_for'] = courseOffering.credit_hours
            info['hours_match'] = courseOffering.credit_hours == required_course.credit_hours.min_credit_hour
            info['comment'] = self.semester_description(student,courseOffering)
        else:
            info['comment'] = None
        return info

    def requirement_block_course_info(self, student, required_course):
        offering_info = lambda offering: {'course_id' : offering.id, 
                                          'semester'  : self.semester_description(student, offering),
                                          'hours_this_semester' : student.hours_this_semester(offering.semester)}
        info = self.make_course_info(student, required_course)
        if info['comment'] is not None:
            info['is_substitute'] = False # TODO: add check that if it is a  substitute
            courseOffering = self.met_courses[required_course]
            info['other_semesters'] = [offering_info(offering)
                                       for offering in CourseOffering.other_offerings(courseOffering)]
        return info

    def courses_in_plan(self, student):
        """
        Creates a default dict of all courses in plan.
        If a course is not in plan defaults to false.
        """
        if not hasattr(self, '_courses_in_plan'):
            self._courses_in_plan = defaultdict(bool)
            for courseOffering in student.planned_courses.all():
                self._courses_in_plan[courseOffering.course] = True
        return self._courses_in_plan

    def is_met_course(self, student, course):
        return self.courses_in_plan(student)[course]

    def unused_courses(self, student):
        """
        Returns a list of unused_course_infos, 
        and unused credit hours.
        """
        return [] # TODO: make unused courses actually return unused courses.


    def grad_audits(self):
        """
        Yields all grad audits so that the parent requirments grad audit 
        directly precede the children grad audits. 
        """
        yield self
        for child in self.children:
            child.grad_audits()

    def requirement_blocks(self, student):
        print 'Hello'
        def make_requirement_comment_fn(req_name):
            def fn(course, req):
                return "{req} is a {req_name} for {course}; the requirment is currently not being met.".format(
                    req=req, course=course, req_name=req_name)
            return fn

        prereq_comment = make_requirement_comment_fn('prereq')
        coreq_comment  = make_requirement_comment_fn('coreq')
                
        block = {}
        for grad_audit in self.grad_audits():
            requirement = grad_audit.requirement
            block['name'] = requirement.name
            block['min_required_credit_hours'] = requirement.min_required_credit_hours
            block['constraint_comments'] = [constraint.name for constraint in requirement.constraints.all()]
            block['courses'] = []
            block['comments'] = []
            for course in requirement.required_courses():
                block['courses'].append(self.requirement_block_course_info(student, course))
                unmet_prereqs = [prereq for prereq in course.prereqs.all() 
                                 if not self.is_met_course(student, prereq)]
                unmet_coreqs   = [coreq for coreq in course.coreqs.all()
                                 if not self.is_met_course(student, coreq)]

                for prereq in unmet_prereqs:
                    block['comments'].append(prereq_comment(course, prereq))
                for coreq in  unmet_coreqs:
                    block['comments'].append(coreq_comment(course, coreq))



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

    def audit(self, courseOfferings, requirement):
        name, arguments = self.parse_constraint_text()
        return getattr(self, name)(courseOfferings, requirement, **arguments)

    def any(self, courses, requirement, **kwargs):
        met_courses = requirement.met_courses(courses, requirement)
        is_satisfied = len(met_courses) >= 1
        return GradAudit(requirement=requirement, is_satisfied=is_satisfied, met_courses=met_courses)


    def all(self, courses, requirement, **kwargs):
        met_courses = requirement.met_courses(courses, requirement)
        is_satisfied = len(met_courses) == len(requirement.required_courses())
        return GradAudit(requirement=requirement, is_satisfied=is_satisfied, met_courses=met_courses)


    def meet_some(self, courses, requirement, **kwargs):
        at_least = int(kwargs['at_least'])
        met_courses = requirement.met_courses(courses, requirement)
        is_satisfied = len(met_courses) >= at_least
        return GradAudit(requirement=requirement, met_courses=met_courses, is_satisfied=is_satisfied)
    

    def min_required_credit_hours (self, courses, requirement, **kwargs):
        at_least = int(kwargs['at_least'])
        course_offerings = [] 
        courses_considered = [] 
        met_courses = requirement.met_courses(courses, requirement)

        def course_has_been_considered(course):
            print("Courses Considered: {}".format("\n".join(str(co) for co in courses_considered)))
            return course in courses_considered

        for met_course in met_courses:
            print("Met course: {}".format(str(met_course)))
            course_offering = met_courses[met_course]
            course = course_offering.course
            if not course_has_been_considered(course):
                course_offerings.append(course_offering)
                courses_considered.append(course_offering.course)
        
        print ("\n".join(str(co) for co in course_offerings))
        is_satisfied = sum(co.credit_hours for co in course_offerings) >= at_least
        return GradAudit(requirement=requirement, is_satisfied=is_satisfied, met_courses=met_courses)

    def different_departments(self, courses, requirement, **kwargs):
        at_least = int(kwargs['at_least'])
        met_courses = requirement.met_courses(courses, requirement)
        courses = [met_course for met_course in met_courses]
        # TODO: Change this. The heuristic is that if a course has different abbreviations
        # it is from different departments. This is not always the case.
        unique_departments = set(course.subject.abbrev for course in courses)
        is_satisfied = len(unique_departments) >= at_least
        return GradAudit(requirement=requirement, met_courses=met_courses, is_satisfied=is_satisfied)

    def all_sub_requirements_satisfied(self, courses, requirement, **kwargs):
        grad_audits = [child.audit(courses) for child in requirement.child_requirements()]
        is_satisfied = all([grad_audit.is_satisfied for grad_audit in grad_audits])
        grad_audit = GradAudit(requirement=requirement, met_course=None, is_satisfied=is_satisfied)
        grad_audit.addChildren(*grad_audits)
        return grad_audit

    def satisfy_some_sub_requirements(self, courses, requirement, **kwargs):
        at_least = int(kwargs['at_least'])
        grad_audits = [child.audit(courses) for child in requirement.child_requirements()]
        satisfied_grad_audits = [grad_audit for grad_audit in grad_audits if grad_audit.is_satisfied]
        is_satisfied = len(satisfied_grad_audits) >= at_least
        grad_audit = GradAudit(requirement=requirement, is_satisfied=is_satisfied, met_course=None)
        grad_audit.addChildren(*grad_audits)
        return grad_audit
    

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

    def satisfied(self, offerings):
        return self.audit(offerings).is_satisfied
        
    def satisfied_grad_audits(self, courses):
        satisfied_grad_audits = []
        for child_requirement in self.child_requirements():
            grad_audit = child_requirement.audit(courses)
            print '\n'.join(str(ga) for ga in grad_audit)
            if grad_audits_satisfied(grad_audit):
                satisfied_grad_audits.append(grad_audit)
            
        return satisfied_grad_audits

    def required_courses(self):
        return list(self.courses.all())

    def all_courses(self):
        """
        Returns a list of all courses. The courses from Requirement, 
        as well as the courses from sub_requriements.
        """
        reqs = self.requirements.all()
        req_courses = [list(req.all_courses()) for req in reqs]

        return self.required_courses() + (list(itertools.chain(*req_courses)))

    def audit(self, courses=None):
        """Returns a GradAudit.
        """
        courses = [] if courses is None else courses
        return self._audit_helper(courses)

    def _audit_helper(self, courses):
        children =  [constraint.audit(courses, self) for constraint in self.constraints.all()]
        is_satisfied = all([child.is_satisfied for child in children])
        gradAudit = GradAudit(requirement=self, met_courses={}, is_satisfied=is_satisfied)
        gradAudit.addChildren(*children)
        return gradAudit

    def child_requirements(self):
        return [child_requirement for child_requirement in self.requirements.all()]

    def met_courses(self, courseOfferings, all=False):
        """
        Returns a a dictionary where the key is the required course, 
        and the value is the offering that meets it. 
        If all is false it only considers courses that meet this requirement.
        otherwise it consideres courses that meet sub requirements.
        """
        if all:
            courses = self.all_courses()
        else:
            courses = self.required_courses()

        met_courses = {}
        for course in courses:
            for co in courseOfferings:
                if co.course in courses:
                    met_courses[course] = co
        return met_courses
            
    class Meta:
        ordering = ['display_name', ]
