#!/usr/bin/python
from keys import *

requirements = [{
NAME : "BS in Computer Engineering 2013-2014",
CONSTRAINTS : ('req_credits(96)', 'req_all'),
REQS : ({
	NAME : "Physics and Engineering Requirements",
    CONSTRAINTS : ('course_all',),
	COURSES : (
        'PHY 211,212',
        'ENP 104,231,252,321,332,333,341,431',
    )},{
	NAME : "Computer Science Requirements",
    CONSTRAINTS : ('course_all',),
	COURSES : (
        'COS 120,121,265,284,311,331,340,381,393,421,491,493,494,495',
    )},{
	NAME : "Mathematics Requirements",
    CONSTRAINTS : ('course_all',),
	COURSES : (
        'MAT 151,215,230,240,251,352',
    )}
)}]
