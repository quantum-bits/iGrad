#!/usr/bin/python
from keys import *

requirements = [{
NAME : "Physics Minor 2013-2014",
CONSTRAINTS : ('req_credits(20)', 'req_all',),
REQS : ({
	NAME : "Minor Requirements",
    CONSTRAINTS : ('course_all',),
	COURSES : (
        'PHY 211,212',
    )},{
	NAME : "Electives",
    CONSTRAINTS : ('course_credits(11)',),
	COURSES : (
        'PHY 300-499',
        'ENP 300-499',
        'ENP 231,252',
    )}
)}]
