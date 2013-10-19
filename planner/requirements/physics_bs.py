#!/usr/bin/python
from keys import *

requirements = [{
NAME : "BS in Physics 2013-2014",
CONSTRAINTS : ('req_credits(92)',),
REQS : ({
	NAME : "Major requirements",
    CONSTRAINTS : ('course_all',),
	COURSES : (
        'PHY 211,212,311,321,322,330,341,342,350,412,413,441,491,493',
    )},{
	NAME : "Major requirements sub",
    CONSTRAINTS : ('course_n(1)',),
	COURSES : (
        'PHY 393,450',
    )},{
	NAME : "Technical electives",
    CONSTRAINTS : ('course_credits(11)',),
	COURSES : (
        'CHE 431,432',
		'ENP 200-499',
		'MAT 310,352,382',
		'PHY 201',
		'PHY 300-499',
    )},{
	NAME : "Additional major requirements",
    CONSTRAINTS : ('course_all','req_n(1)',),
    REQS : (sub_cos, sub_enp,),
	COURSES : (
        'CHE 211,212',
        'COS 120',
        'MAT 151,230,240,245,251',
    )},{
	NAME : "Additional major requirements sub",
    CONSTRAINTS : ('course_n(1)',),
	COURSES : (
        'IAS 231',
        'NAS 480',
    )}
)}]

sub_cos = {
	NAME : "COS104 option",
    CONSTRAINTS : ('course_all',),
	COURSES : (
        'COS 104',
)}

sub_enp = {
	NAME : "ENP104+105 option",
    CONSTRAINTS : ('course_all',),
	COURSES : (
        'ENP 104,105',
)}
