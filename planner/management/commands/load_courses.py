from django.core.management.base import BaseCommand, CommandError
from planner.models import Course, Subject, CreditHour, SemesterName
import xlrd
import re

class Command(BaseCommand):
    def handle(self, *args, **options):
        filename = args[0]
        try:
            workbook = xlrd.open_workbook(filename)
        except IOError: 
            print '"{}" does not exist.'.format(filename)
        
        sheet = workbook.sheet_by_index(0)
        title_row = sheet.row_values(1)
        

        default_credit_hour = CreditHour.objects.get(value='3')
        fall = SemesterName.objects.get(name='Fall')
        spring = SemesterName.objects.get(name='Spring')

        for i in xrange(2, sheet.nrows):
            row = sheet.row_values(i)
            sub_abbrev, title, number = self.extract_data(row)
            if self.valid(sub_abbrev, title, number):
                try:
                    subject = Subject.objects.get(abbrev=sub_abbrev)
                except Subject.DoesNotExist:
                    subject = Subject.objects.create(abbrev=sub_abbrev, name=sub_abbrev)

                try:
                    course = Course.objects.get(subject=subject, number=int(number))
                except Course.DoesNotExist:
                    course = Course.objects.create(subject=subject, number=int(number),
                                                   title=title, credit_hours=default_credit_hour, 
                                                   schedule_year='B')
                    course.schedule_semester.add(fall)
                    course.schedule_semester.add(spring)
                    

    def extract_data(self, row):
        "Returns subject, title, course number."
        subject = row[1]
        title = row[3]
        number = row[2]
        
        return subject, title, number

    def valid(self, subject, title, number):
        if re.match(r'^[A-Z]{3}$', subject) is None: return False
        if re.match(r'^[ ]*$', title): return False
        if re.match(r'^[0-9]{3}$', number) is None: return False
        return True
            
        

        
