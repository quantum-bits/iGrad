#!/usr/bin/python

import os

requirements = (
    'computer_engineering_bs', 
    'computer_science_bs',
    'engineering_physics_bs',
    'environmental_engineering_bs',
    'foundation_core',
    'mathematics_interdisciplinary_bs',
    'physics_ba',
    'physics_bs',
    'physics_minor',
)

for req in requirements: 
    os.system('./manage.py load_reqs {}'.format(req))


with open('courses.txt', 'r') as courses_f:
    courses = [c for c in courses_f]

courses = sorted(list(set(courses)))
with open('requirements_courses.txt', 'w') as courses_f:
    for c in courses:
        courses_f.write(c) 


