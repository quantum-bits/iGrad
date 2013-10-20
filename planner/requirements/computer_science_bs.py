#!/usr/bin/python
from keys import *

sub_graphics = {
	NAME : "Graphics",
    CONSTRAINTS : ('course_all',),
	COURSES : (
        'COS 314,350,351,424,425',
        'SYS 214',
)}
sub_isystems = {
	NAME : "Intelligent Systems",
    CONSTRAINTS : ('course_all',),
	COURSES : (
        'COS 280,351,380',
        'SYS 352,411',
)}
sub_scicomp = {
	NAME : "Scientific Computing",
    CONSTRAINTS : ('course_all',),
	COURSES : (
        'MAT 230,240,245,251,310',
)}
sub_studio = {
	NAME : "Software Studio",
    CONSTRAINTS : ('course_all',),
	COURSES : (
        'COS 340,371,372,471,472',
)}

requirements = [{
NAME : "BS in Computer Science 2013-2014",
CONSTRAINTS : ('req_credits(86)', 'req_all'),
REQS : ({
	NAME : "Core Requirements",
    CONSTRAINTS : ('course_all',),
	COURSES : (
        'COS 120,121,143,243,265,284,310,320,382,435,452,493',
        'MAT 151,215',
        'SYS 101',
    )},{
	NAME : "Core Requirements Sub 1",
    CONSTRAINTS : ('course_n(1)',),
	COURSES : (
        'COS 311,321',
    )},{
	NAME : "Core Requirements Sub 2",
    CONSTRAINTS : ('course_n(2)',),
	COURSES : (
        'COS 381,421,436',
    )},{
	NAME : "Core Requirements Sub 3",
    CONSTRAINTS : ('course_n(1)',),
	COURSES : (
        'MAT 201,352',
    )},{
	NAME : "Electives",
    EXCLUDE : ('COS 393',),
	COURSES : (
        'COS 230,240,280',
        'COS 300-499',
        'SYS 214,352,401,402,403,411',
    )},{
	NAME : "Concentration",
    CONSTRAINTS : ('req_n(1)',),
    REQS : (sub_graphics,sub_isystems,sub_scicomp,sub_studio,)
	}
)}]

