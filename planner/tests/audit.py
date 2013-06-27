from django.test import TestCase
from planner.campus_models import Course, Requirement, CourseOffering

class RequirementTest(TestCase):
    def test_any_prereq(self):
        cos310 = Course.objects.get(subject__abbrev = 'COS', number = 310)
        cos_300_courses = Course.objects.filter(subject__abbrev = 'COS', number__gte = 300)
        cos_300_courses = cos_300_courses.exclude(subject__abbrev = 'COS', number = 310)

        cos_300_cos = []
        for cos_300_course in cos_300_courses:
            cos_300_cos.append(CourseOffering.objects.filter(course=cos_300_course)[0])

        cos310_prereqs = cos310.prereqs.all()
        cos310_co = CourseOffering.objects.filter(course=cos310)[0]

        for prereq in cos310_prereqs:
            for co in cos_300_cos:
                satisfied = prereq.satisfied([co])
                self.assertTrue(satisfied)
            self.assertFalse(prereq.satisfied([cos310_co]))
                
    def test_all_prereq(self):
        cos120 = Course.objects.get(subject__abbrev = 'COS', number = 120)
        cos120_co = CourseOffering.objects.filter(course=cos120)[0]
        cos121 = Course.objects.get(subject__abbrev = 'COS', number = 121)
        cos121_prereqs = cos121.prereqs.all()

        for prereq in cos121_prereqs:
            self.assertTrue(prereq.satisfied([cos120_co]))

        for prereq in cos121_prereqs:
            self.assertFalse(prereq.satisfied())

    def test_meet_two(self):
        requirement = Requirement.objects.get(name='CS Theory Courses')
        cos_320 = Course.objects.get(subject__abbrev = 'COS', number = 320)
        cos_320_co = CourseOffering.objects.filter(course=cos_320)[0]
        cos_382 = Course.objects.get(subject__abbrev = 'COS', number = 382)
        cos_382_co = CourseOffering.objects.filter(course=cos_382)[0]
        cos_435 = Course.objects.get(subject__abbrev = 'COS', number = 435)
        cos_435_co = CourseOffering.objects.filter(course=cos_435)[0]

        satisfied = requirement.satisfied([cos_320_co, cos_382_co, cos_435_co])
        self.assertTrue(satisfied)
        self.assertFalse(requirement.satisfied([cos_320_co]))
        
    def test_sub_requirements_retrieval(self):
        science_gen_ed = Requirement.objects.get(name = 'Science Gen Eds')
        self.assertEqual(len(science_gen_ed.requirements.all()), 3, 'Science Gen Ed should have 3 sub requirements.')
        self.assertEqual(len(science_gen_ed.sub_categories()), 3, 'Science Gen Ed should have 3 sub categories.')
        
                                              
    def test_multilevel_requirments(self):
        science_gen_ed = Requirement.objects.get(name='Science Gen Eds')
        geo_210 = Course.objects.get(subject__abbrev = 'GEO', number = 210)
        geo_210_co = CourseOffering.objects.filter(course = geo_210)[0]
        bio_100 = Course.objects.get(subject__abbrev = 'BIO', number = 100)
        bio_100_co = CourseOffering.objects.filter(course = bio_100)[0]
        
        che_120 = Course.objects.get(subject__abbrev = 'CHE', number = 120)
        che_120_co, che_120_co1 = CourseOffering.objects.filter(course = che_120)[0:2]

        self.assertTrue(science_gen_ed.satisfied([geo_210_co, bio_100_co]))
        self.assertFalse(science_gen_ed.satisfied([che_120_co]), "One course can't count twice.")
        self.assertFalse(science_gen_ed.satisfied([che_120_co, che_120_co1]), "Course offering courses should only count once.")
        self.assertTrue(science_gen_ed.satisfied([geo_210_co, che_120_co, bio_100_co]))


    def test_courses_and_requirments_block(self):
        """Test requirements blocks that have both courses
           and sub requirement blocks.
        """
        stewardship_req = Requirement.objects.get(name='Stewardship of the Body Gen Eds')
        
        php_100    = Course.objects.get(subject__abbrev = 'PHP', number = 100)
        php_100_co = CourseOffering.objects.filter(course=php_100)[0]
        
        php_200    = Course.objects.get(subject__abbrev = 'PHP', number = 200)
        php_200_co = CourseOffering.objects.filter(course=php_200)[0]

        self.assertTrue(stewardship_req.satisfied([php_100_co, php_200_co]))

    
    def test_different_department_constraint(self):
        social_science_gen_eds = Requirement.objects.get(name='Social Science Gen Eds')
        eco_190 = Course.objects.get(subject__abbrev = 'ECO', number = 190)
        eco_190_co = CourseOffering.objects.filter(course = eco_190)[0]
        eco_201 = Course.objects.get(subject__abbrev = 'ECO', number = 201)
        eco_201_co = CourseOffering.objects.filter(course = eco_201)[0]
        geo_230 = Course.objects.get(subject__abbrev = 'GEO', number = 230)
        geo_230_co = CourseOffering.objects.filter(course = geo_230)[0]

        self.assertTrue(social_science_gen_eds.satisfied([eco_190_co, geo_230_co]))
        self.assertFalse(social_science_gen_eds.satisfied([eco_201_co, eco_201_co]))
