from django.test import TestCase
from planner.campus_models import Course, CourseOffering
from planner.grad_audit_models import Requirement


class RequirementTest(TestCase):

    def _get_course_offering(self, course):
        return CourseOffering.objects.filter(course=course)[0]

    
    def test_met_courses(self):
        cos_104 = Course.objects.get(subject__abbrev='COS', number=104)
        cos_106 = Course.objects.get(subject__abbrev='COS', number=106)
        cos_104_co = self._get_course_offering(cos_104)
        cos_106_co = self._get_course_offering(cos_106)
        
        requirement = Requirement.objects.get(name='Computer Science Gen Eds')
        met_courses = requirement.met_courses([cos_104_co, cos_106_co])
        self.assertEqual(len(met_courses), 2)

        

    def assertPrereqsSatisfied(self, prereqs, course_offerings, message = None):
        def unmet_requirement_explanation(gradAudit):
            requirement_info = "Requirement '{}' not satisfied".format(gradAudit.requirement)
            constraint_info = "Constrainsts:\n{}".format('\n'.join(gradAudit.constraint_messages))
            met_courses_info = "Met courses:\n{}".format('\n'.join("{} => {}".format(course_offering, course)
                                                                   for course,course_offering in gradAudit.met_courses.items()))
            courseOfferings_info = "Course Offerings:\n{}".format('\n'.join(str(co) for co in course_offerings))

            return '\n'.join([requirement_info, constraint_info, met_courses_info, courseOfferings_info])
                                                        
        for prereq in prereqs:
            gradAudit, unused_courses = prereq.audit(course_offerings)
            self.assertTrue(gradAudit.is_satisfied, unmet_requirement_explanation(gradAudit))

    def assertPrereqsUnsatisfied(self, prereqs, course_offerings, message = None):
        if message is None: message = 'Prereqs should not be satisfied.'
        for prereq in prereqs:
            gradAudit, unused_courses = prereq.audit(course_offerings)
            self.assertFalse(gradAudit.is_satisfied, message)

    def test_any_prereq(self):
        
        cos310 = Course.objects.get(subject__abbrev = 'COS', number = 310)
        cos300_courses = Course.objects.filter(subject__abbrev = 'COS', number__gte = 300)
        cos300_courses = cos300_courses.exclude(subject__abbrev = 'COS', number = 310)

        cos300_course_offerings = [self._get_course_offering(course) for course in cos300_courses]

        cos310_prereqs = cos310.prereqs.all()
        cos310_co = self._get_course_offering(cos310)

        
        for prereq in cos310_prereqs:
            for co in cos300_course_offerings:
                gradAudit, unused_courses = prereq.audit([co])
                self.assertTrue(gradAudit.is_satisfied, "300-level course should meet requirement.")
                

            gradAudit, unused_courses = prereq.audit([cos310_co])
            self.assertFalse(gradAudit.is_satisfied, "COS 310 should not satisfy requirement for COS 310")

                
    def test_all_prereq(self):
        cos120 = Course.objects.get(subject__abbrev = 'COS', number = 120)
        cos120_co = self._get_course_offering(cos120)
        cos121 = Course.objects.get(subject__abbrev = 'COS', number = 121)
        cos121_prereqs = cos121.prereqs.all()

        self.assertPrereqsSatisfied(cos121_prereqs, [cos120_co])
        self.assertPrereqsUnsatisfied(cos121_prereqs, [])

    def test_meet_two(self):
        requirement = Requirement.objects.get(name='CS Theory Courses')
        cos320 = Course.objects.get(subject__abbrev = 'COS', number = 320)
        cos320_co = self._get_course_offering(cos320)
        cos382 = Course.objects.get(subject__abbrev = 'COS', number = 382)
        cos382_co = self._get_course_offering(cos382)
        cos435 = Course.objects.get(subject__abbrev = 'COS', number = 435)
        cos435_co = self._get_course_offering(cos435)

        self.assertPrereqsSatisfied([requirement], [cos320_co, cos382_co, cos435_co])
        self.assertPrereqsUnsatisfied([requirement], [cos320_co])
        
    def test_sub_requirements_retrieval(self):
        science_gen_ed = Requirement.objects.get(name = 'Science Gen Eds')
        self.assertEqual(len(science_gen_ed.requirements.all()), 3, 'Science Gen Ed should have 3 sub requirements.')
        self.assertEqual(len(science_gen_ed.child_requirements()), 3, 'Science Gen Ed should have 3 sub categories.')
        
                                              
    def test_multilevel_requirments(self):
        science_gen_ed = Requirement.objects.get(name='Science Gen Eds')
        geo210 = Course.objects.get(subject__abbrev = 'GEO', number = 210)
        geo210_co = self._get_course_offering(geo210)
        bio100 = Course.objects.get(subject__abbrev = 'BIO', number = 100)
        bio100_co = self._get_course_offering(bio100)
        
        che120 = Course.objects.get(subject__abbrev = 'CHE', number = 120)
        che120_co, che120_co1 = CourseOffering.objects.filter(course = che120)[0:2]

        self.assertPrereqsSatisfied([science_gen_ed], [geo210_co, bio100_co])
        self.assertPrereqsUnsatisfied([science_gen_ed], [che120_co], "One course can't count twice.")
        self.assertPrereqsUnsatisfied([science_gen_ed], [che120_co, che120_co1], "Course offering courses should only count once.")
        self.assertPrereqsSatisfied([science_gen_ed], [geo210_co, che120_co, bio100_co])


    def test_courses_and_requirments_block(self):
        """Test requirements blocks that have both courses
           and sub requirement blocks.
        """
        stewardship_req = Requirement.objects.get(name='Stewardship of the Body Gen Eds')
        
        php100    = Course.objects.get(subject__abbrev = 'PHP', number = 100)
        php100_co = self._get_course_offering(php100)
        
        php200    = Course.objects.get(subject__abbrev = 'PHP', number = 200)
        php200_co = self._get_course_offering(php200)

        self.assertPrereqsSatisfied([stewardship_req],[php100_co, php200_co])

    
    def test_different_department_constraint(self):
        social_science_gen_eds = Requirement.objects.get(name='Social Science Gen Eds')
        eco190 = Course.objects.get(subject__abbrev = 'ECO', number = 190)
        eco190_co = self._get_course_offering(eco190)
        eco201 = Course.objects.get(subject__abbrev = 'ECO', number = 201)
        eco201_co = self._get_course_offering(eco201)
        geo230 = Course.objects.get(subject__abbrev = 'GEO', number = 230)
        geo230_co = self._get_course_offering(geo230)


        self.assertPrereqsSatisfied([social_science_gen_eds], [eco190_co, geo230_co])
        self.assertPrereqsUnsatisfied([social_science_gen_eds], [eco201_co, eco190_co])

