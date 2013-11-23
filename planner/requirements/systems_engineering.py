#!/usr/bin/python

from keys import *


major_courses = ('ECO 201',
                 'ENS 200',
                 'ENT 420',
                 'IAS 330',
                 'MAT 251,352,382',
                 'SYS 214,320,390,392,393,394,401,402,403,405',)

requirements = [{
        NAME : 'Systems Engineering', 
        CONSTRAINTS : ('req_credits(105)', 'req_all',),
        REQS : ({NAME : 'Systems Engineering Core', 
                 CONSTRAINTS : ('course_all',),
                 COURSES : ('CHE 211', 'COS 120,143', 'ENP 104,105,252',
                            'MAT 151,230,240', 'PHY 211,212', 'SYS 101',)},
                {NAME : 'Systems Engineering Additional Requirements', 
                 CONSTRAINTS : ('course_all', 'req_all',),
                 COURSES : ('ENP 231,301',),
                 REQS : ({NAME : 'Systems Engineering Optional Course', 
                          CONSTRAINTS : ('course_n(1)',),
                          COURSES : ('ENP 302,351',)},)},
                {NAME : 'Systems Engineering Major Courses', 
                 CONSTRAINTS : ('course_all', 'req_all',),
                 COURSES : major_courses, 
                 REQS : ({NAME : 'Systems Engineering Major Courses Optional Courses',
                          CONSTRAINTS : ('course_n(1)',),
                          COURSES : ('ENP 491', 'SYS 410',)},)},)}]
