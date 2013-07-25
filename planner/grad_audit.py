#!/usr/bin/python
from collections import deque, namedtuple
from models import CourseOffering

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
        info['credit_hours'] = required_course.possible_credit_hours()
        info['sp'] = required_course.sp
        info['cc'] = required_course.cc
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
        block = {}
        for grad_audit in self.grad_audits():
            block['name'] = grad_audit.requirement.name
            block['min_required_credit_hours'] = grad_audit.requirement.min_required_credit_hours
            block['comments'] = [constraint.name for constraint in requirement.constraints.all()]
            block['courses'] = [self.requirement_block_course_info(student, course)
                                for course in requirement.required_courses]
        block['unused_courses'] = self.unused_courses(student)







