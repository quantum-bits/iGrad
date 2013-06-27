#!/usr/bin/python
from collections import namedtuple
import collections

MetCourse = namedtuple('MetCourse', 'required_course, course_offering')

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
