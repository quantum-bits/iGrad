from django.test import TestCase
from planner.campus_models import Course, Requirement

class RequirementTest(TestCase):
    def test_any_prereq(self):
        cos310 = Course.objects.get(subject__abbrev = 'COS', number = 310)
        cos_300_courses = Course.objects.filter(subject__abbrev = 'COS', number__gte = 300)
        cos_300_courses = cos_300_courses.exclude(subject__abbrev = 'COS', number = 310)
        cos310_prereqs = cos310.prereqs.all()

        for prereq in cos310_prereqs:
            for course in cos_300_courses:
                satisfied = prereq.satisfied(course)
                self.assertTrue(satisfied)
            self.assertFalse(prereq.satisfied(cos310))
                
    def test_all_prereq(self):
        cos120 = Course.objects.get(subject__abbrev = 'COS', number = 120)
        cos121 = Course.objects.get(subject__abbrev = 'COS', number = 121)
        cos121_prereqs = cos121.prereqs.all()

        for prereq in cos121_prereqs:
            self.assertTrue(prereq.satisfied(cos120))

        for prereq in cos121_prereqs:
            self.assertFalse(prereq.satisfied())

    def test_meet_two(self):
        requirement = Requirement.objects.get(name='CS Theory Courses')
        cos_320 = Course.objects.get(subject__abbrev = 'COS', number = 320)
        cos_382 = Course.objects.get(subject__abbrev = 'COS', number = 382)
        cos_435 = Course.objects.get(subject__abbrev = 'COS', number = 435)

        satisfied = requirement.satisfied(cos_320, cos_382, cos_435)
        self.assertTrue(satisfied)
        self.assertFalse(requirement.satisfied(cos_320))
        
    def test_sub_requirements_retrieval(self):
        science_gen_ed = Requirement.objects.get(name = 'Science Gen Eds')
        self.assertEqual(len(science_gen_ed.requirements.all()), 3, 'Science Gen Ed should have 3 sub requirements.')
        self.assertEqual(len(science_gen_ed.sub_categories()), 3, 'Science Gen Ed should have 3 sub categories.')
        
                                              
    def test_multilevel_requirments(self):
        science_gen_ed = Requirement.objects.get(name='Science Gen Eds')
        geo_210 = Course.objects.get(subject__abbrev = 'GEO', number = 210)
        bio_100 = Course.objects.get(subject__abbrev = 'BIO', number = 100)
        
        che_120 = Course.objects.get(subject__abbrev = 'CHE', number = 120)

        self.assertTrue(science_gen_ed.satisfied(geo_210, bio_100))
        self.assertFalse(science_gen_ed.satisfied(che_120))
        self.assertTrue(science_gen_ed.satisfied(geo_210, che_120, bio_100))

    def test_courses_and_requirments_block(self):
        """Test requirements blocks that have both courses
           and sub requirement blocks.
        """
        stewardship_req = Requirement.objects.get(name='Stewardship of the Body Gen Eds')
        php_100 = Course.objects.get(subject__abbrev = 'PHP', number = 100)
        php_200 = Course.objects.get(subject__abbrev = 'PHP', number = 200)

        self.assertTrue(stewardship_req.satisfied(php_100, php_200))

    
    def test_different_department_constraint(self):
        social_science_gen_eds = Requirement.objects.get(name='Social Science Gen Eds')
        eco_190 = Course.objects.get(subject__abbrev = 'ECO', number = 190)
        eco_201 = Course.objects.get(subject__abbrev = 'ECO', number = 201)
        geo_230 = Course.objects.get(subject__abbrev = 'GEO', number = 230)

        self.assertTrue(social_science_gen_eds.satisfied(eco_190, geo_230))
        self.assertFalse(social_science_gen_eds.satisfied(eco_201, eco_201))

