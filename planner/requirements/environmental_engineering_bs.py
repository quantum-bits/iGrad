#!/usr/bin/python
from keys import *

requirements = [{
NAME : "BS in Environmental Engineering 2013-2014",
CONSTRAINTS : ('req_credits(99)', 'req_all',),
REQS : ({
	NAME : "Physics Requirements",
    CONSTRAINTS : ('course_all',),
	COURSES : (
        'ENP 104,105,231,252,351,355,392,491,492,493,494',
        'PHY 211,212',
    )},{
	NAME : "Physics Requirements sub",
    CONSTRAINTS : ('course_credits(3)',),
    EXCLUDE : ('BIO 100,200',),
	COURSES : (
        'ENS 204',
        'MAT 210',
        'MAT 245',
        'MAT 310',
        'MAT 352',
        'BIO 101-499',
        'CHE 300-499',
        'ENP 300-499',
        'ENS 300-499',
        'PHY 300-499',
    )},{
	NAME : "Environmental Science Requirements",
    CONSTRAINTS : ('course_all',),
	COURSES : (
        'ENS 231,251,355,402',
    )},{
	NAME : "Environmental Science Sub",
    CONSTRAINTS : ('course_n(1)',),
	COURSES : (
        'ENS 393',
        'ENP 393',
    )},{
	NAME : "Environmental Science Sub 2",
    CONSTRAINTS : ('course_credits(8)',),
	COURSES : (
        'CHE 320',
        'ENS 341,361,362,363',
    )},{
	NAME : "Mathematics Requirements",
    CONSTRAINTS : ('course_all',),
	COURSES : (
        'MAT 151,230,240,251',
    )},{
	NAME : "Additional Requirements",
    CONSTRAINTS : ('course_all',),
	COURSES : (
        'CHE 211,212',
        'COS 120',
        'ECO 201',
        'IAS 330',
    )}
)}]
