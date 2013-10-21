#!/usr/bin/python
import os

for year in range(2013, 2020):
    start_year = year
    end_year = year + 1
    print 'Adding offerings for {} - {}'.format(start_year, end_year)
    os.system('./manage.py make_course_offerings {} {}'.format(start_year, end_year))

print 'Done adding courses.'
