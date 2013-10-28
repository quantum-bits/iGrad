from django.test import TestCase
from planner.campus_models import AcademicYear

class AcademicYearTest(TestCase):
    

    def test__cmp__(self):
        before = AcademicYear.objects.get(begin_on__year=2009)
        year = AcademicYear.objects.get(begin_on__year=2010)
        after = AcademicYear.objects.get(begin_on__year=2011)

        self.assertFalse(year > year, 'Year should not be greater than itself.')
        self.assertEqual(year, year, 'Year should be equal to itself.')
        self.assertTrue(before < year, 'Before should be less than year.')
        self.assertTrue(year > before, 'Year should be greater than before.')

        self.assertTrue(after > year, 'After should be greater than year.')
        self.assertTrue(year < after, 'Year should be less than after.')
        
        self.assertTrue(before < after, 'Before should be less than after.')

