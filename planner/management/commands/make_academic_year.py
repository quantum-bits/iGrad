from django.core.management.base import BaseCommand, CommandError
from planner.models import AcademicYear
import datetime 

class Command(BaseCommand):
    args = 'start_year, end_year'
    help = 'Create an academic year for start_year - end_year if it does not exist'
    
    def handle(self, *args, **options):
        start_year, end_year = args
        start_year = int(start_year)
        end_year = int(end_year)
        try:
            year = AcademicYear.objects.get(begin_on__year=start_year,
                                            end_on__year = end_year)
            print "Academic Year for: {} already exists.".format(year)
        except AcademicYear.DoesNotExist:
            year = AcademicYear.objects.create(begin_on=datetime.date(start_year, 8,1), 
                                               end_on=datetime.date(end_year, 7, 31))
            print "Created new Academic Year for: {}".format(year)
