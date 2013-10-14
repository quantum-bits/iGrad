#!/usr/bin/python

NAME = 'Name'
COURSES = 'Course'
SUB_REQ = 'SubRequirements'

MAJOR_COURSES = (
    'PHY 211',
    'PHY 212',
    'PHY 311',
    'PHY 321', 
    'PHY 322',
    'PHY 330',
    'PHY 341',
    'PHY 342',
    'PHY 350',
    'PHY 412',
    'PHY 413',
    'PHY 441', 
    'PHY 491',
    'PHY 493',
)



r_MAJOR_REQ_SUB = {NAME : 'Physics (BS) Major Requirements Sub' ,
                   COURSES : ('PHY 393', 'PHY 450',)}

r_MAJOR_REQUIREMENTS = {NAME : 'Physics (BS) Major Requirements',
                        COURSES : MAJOR_COURSES,
                        SUB_REQ : [r_MAJOR_REQ_SUB]}

TECHNICAL_ELECTIVES_COURSES = (
    'CHE 431',
    'CHE 432',
    'ENP 200-499',
    'MAT 310',
    'MAT 252',
    'MAT 382',
    'PHY 201',
    'PHY 300-499',
)

r_TECHNICAL_ELECTIVES = {NAME : 'Physics (BS) Technical Electives', 
                         COURSES : TECHNICAL_ELECTIVES_COURSES}

ADDITIONAL_MAJOR_REQ_COURSES = (
    'CHE 211',
    'CHE 212',
    'COS 120',
    'ENP 104',
    'ENP 105',
    'MAT 151',
    'MAT 230',
    'MAT 240',
    'MAT 245',
    'MAT 251',
)

r_ADDITIONAL_MAJOR_REQUIREMENTS_SUB = {NAME : 'Physics (BS) Additional Major Requirements Sub', 
                                       COURSES : ('IAS 231', 'NAS 480',)}

r_ADDITIONAL_MAJOR_REQUIREMENTS = {NAME : 'Physics (BS) Additional Major Requirements',
                                   COURSES : ADDITIONAL_MAJOR_REQ_COURSES, 
                                   SUB_REQ : [r_ADDITIONAL_MAJOR_REQUIREMENTS_SUB]}

r_PHYSICS_BS = {NAME : 'Physics (BS)',
                SUB_REQ: [r_MAJOR_REQUIREMENTS,
                          r_TECHNICAL_ELECTIVES, 
                          r_ADDITIONAL_MAJOR_REQUIREMENTS]}

requirements = [r_MAJOR_REQ_SUB, r_MAJOR_REQUIREMENTS, r_TECHNICAL_ELECTIVES, r_ADDITIONAL_MAJOR_REQUIREMENTS_SUB, r_ADDITIONAL_MAJOR_REQUIREMENTS, r_PHYSICS_BS]

