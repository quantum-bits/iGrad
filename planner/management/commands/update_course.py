from django.core.management.base import BaseCommand, CommandError
from planner.models import Course, CreditHour

class Command(BaseCommand):
    help = 'Update course credit hour.'

    def handle(self, *args, **kwargs):
        try:
            course_abbrev, number, credit_hours = args
        except ValueError:
            raise CommandError('Need to supply a coures abbreviation, number, and credit hour.')

        try:
            course = Course.objects.get(subject__abbrev=course_abbrev.upper(), number=number)
        except Course.DoesNotExist:
            raise CommandError('Course: {} Does not exist.'.format(course_abbrev.upper() + number))
        
        credit_hours, _ = CreditHour.objects.get_or_create(name=credit_hours, value=credit_hours)
        course.credit_hours = credit_hours
        course.save()

        print 'Course: {} now has {} credit_hour(s)'.format(course, credit_hours)
    
        
