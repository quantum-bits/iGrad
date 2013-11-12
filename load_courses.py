#!/usr/bin/python

import os
import csv

from collections import namedtuple

CourseInfo = namedtuple('CourseInfo', 'abbrev,number, credit_hours')


for course in csv.reader(open('courses.csv', 'rb')):
    if course:
        abbrev, number = course[0].split(' ')
        credit_hours = course[1]
        args = ' '.join([abbrev, number, credit_hours])
        os.system('python manage.py update_course ' + args)

        

