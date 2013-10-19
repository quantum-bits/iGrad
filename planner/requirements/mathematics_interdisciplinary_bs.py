#!/usr/bin/python
from keys import *

requirements = [{
NAME : "BS in Mathematics-Interdisciplinary 2013-2014",
CONSTRAINTS : ('req_credits(52)',),
REQS : ({
	NAME : "Major requirements",
    CONSTRAINTS : ('course_all',),
	COURSES : (
        'MAT 180,230,240,245,251,255,310,352,382,392,393,493',
    )},{
	NAME : "Major requirements sub",
    CONSTRAINTS : ('course_n(1)',),
	COURSES : (
        'MAT 340,455',
    )},{
	NAME : "Electives",
    CONSTRAINTS : ('course_credits(3)',),
    EXCLUDE : ('MAT 301,302',),
	COURSES : (
        'MAT 215-499',
    )},{
	NAME : "Additional major requirements",
    CONSTRAINTS : ('course_all',),
	COURSES : (
        'COS 120',
    )},{
	NAME : "Additional major requirements sub",
    CONSTRAINTS : ('course_n(1)',),
	COURSES : (
        'CHE 201,211',
        'PHY 211,212',
    )}
)}]
