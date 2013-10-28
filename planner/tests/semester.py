from django.test import TestCase
from planner.campus_models import Semester

class AcademicYearTest(TestCase):
    

    def get_semester(self, semesterName, year):
        return Semester.objects.get(name__name=semesterName, year__begin_on__year=year)

    def test__cmp__(self):
        
        fall_2009 = self.get_semester('Fall', 2009)
        j_term_2009 = self.get_semester('J-Term', 2009)
        spring_2009 = self.get_semester('Spring', 2009)
        summer_2009 = self.get_semester('Summer', 2009)

        
        fall_2010 = self.get_semester('Fall', 2010)
        spring_2011 = self.get_semester('Spring', 2011)
        j_term_2012 = self.get_semester('J-Term', 2012)

        self.assertTrue(fall_2009 < j_term_2009, 'Fall 2009 should come before J-Term 2009')
        self.assertTrue(j_term_2009 < spring_2009, 'J-Term should come before Spring 2009')
        self.assertTrue(spring_2009 < summer_2009, 'Spring 2009 should come before Summer 2009')
        
        self.assertEqual(fall_2009, fall_2009, 'A semester should be equal to itself.')

        self.assertTrue(fall_2010 < spring_2011, 'Fall 2010 should come before Spring 2011')
        self.assertTrue(j_term_2012 > fall_2010, 'J-Term 2012 should come after Fall 2010')
        self.assertTrue(j_term_2012 > spring_2011, 'J-Term 2012 should come after Spring 2011')  
        
        

        
