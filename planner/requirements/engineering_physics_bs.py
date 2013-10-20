#!/usr/bin/python
from keys import *

sub_tier_a = {
	NAME : "Tier A",
    CONSTRAINTS : ('course_credits(15)',),
	COURSES : (
        'ENP 302,321,333,341,355,357,394',
        'COS 121,230,331,313',
        'SYS 390,403',
)}

requirements = [{
NAME : "BS in Engineering Physics 2013-2014",
CONSTRAINTS : ('req_credits(104)', 'req_all',),
REQS : ({
	NAME : "Science and math requirements",
    CONSTRAINTS : ('course_all',),
	COURSES : (
		'CHE 211',
        'MAT 151,230,240,251',
        'PHY 211,212,311,321,341',
    )},{
	NAME : "Science and math requirements sub",
    CONSTRAINTS : ('course_n(1)',),
	COURSES : (
		'NAS 480',
		'IAS 231',
    )},{
	NAME : "Engineering requirements",
    CONSTRAINTS : ('course_all',),
	COURSES : (
        'COS 120',
        'ENP 104,105',
        'ENP 231,252,301,332,351,352,392,393,491,492,493,494',
    )},{
	NAME : "Additional requirements",
    CONSTRAINTS : ('course_all',),
	COURSES : (
		'ECO 201',
		'IAS 330',
    )},{
	NAME : "Tier B",
    CONSTRAINTS : ('req_all','req_credits(18)',),
    REQS : (sub_tier_a,),
	COURSES : (
        'ENP 345',
        'ENT 422',
        'MAT 245,352',
        'PHY 322,342,412,441',
    )}
)}]


