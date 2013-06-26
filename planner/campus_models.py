from common_models import *
from django.db import models
from itertools import chain
from collections import namedtuple


import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
fileHandler = logging.FileHandler('campus_models.log', mode='w')
fileHandler.setLevel(logging.DEBUG)
logger.addHandler(fileHandler)


class University(StampedModel):
    """University. Top-level organizational entity."""
    name = models.CharField(max_length=100)
    url = models.URLField()

    class Meta:
        verbose_name_plural = 'universities'

    def __unicode__(self):
        return self.name


class School(StampedModel):
    """School within university. Some institutions refer to this as a 'college' or 'division'."""
    name = models.CharField(max_length=100)
    university = models.ForeignKey(University, related_name='schools')
    dean = models.OneToOneField('FacultyMember', blank=True, null=True)

    def __unicode__(self):
        return self.name


class Department(models.Model):
    """Academic department"""
    # not every department has a convient abbreviation.
    abbrev = models.CharField(max_length=10, blank=True)
    name = models.CharField(max_length=100)
    school = models.ForeignKey(School, related_name='departments')
    chair = models.OneToOneField('FacultyMember', blank=True, null=True,
                                 related_name='department_chaired')

    def __unicode__(self):
        return self.name



class FacultyMember(Person):
    RANK_CHOICES = (('Inst', 'Instructor'),
                    ('Adj', 'Adjunct Professor'),
                    ('Asst', 'Assistant Professor'),
                    ('Assoc', 'Associate Professor'),
                    ('Full', 'Professor'))

    university = models.ForeignKey(University, related_name='faculty')
    faculty_id = models.CharField(max_length=25)
    department = models.ForeignKey(Department, related_name='faculty')
    rank = models.CharField(max_length=8, choices=RANK_CHOICES)


class StaffMember(Person):
    university = models.ForeignKey(University, related_name='staff')
    staff_id = models.CharField(max_length=25)
    department = models.ForeignKey(Department, related_name='staff')


class AcademicYear(models.Model):
    begin_on = models.DateField(unique_for_year=True)
    end_on = models.DateField(unique_for_year=True)

    class Meta:
        ordering = [ 'begin_on' ]

    def __unicode__(self):
        return '{0}-{1}'.format(self.begin_on.year, self.end_on.year)
    

class SemesterName(models.Model):
    """Name for a semester. Using model here may be overkill, but it provides a nice way in
    which to order the semesters throughout the academic year.
    """
    seq = models.PositiveIntegerField(default=10)
    name = models.CharField(max_length=40)

    class Meta:
        ordering = ['seq']

    @property
    def fall(self):
        return self.name == 'Fall'
    
    @property
    def j_term(self):
        return self.name == 'J-Term'

    @property
    def spring(self):
        return self.name == 'Spring'

    @property
    def summer(self):
        return self.name == 'Summer'


    def __unicode__(self):
        return self.name


class Semester(models.Model):
    """Instance of a single semester in a given academic year."""
    name = models.ForeignKey(SemesterName)
    year = models.ForeignKey(AcademicYear, related_name='semesters')
    begin_on = models.DateField()
    end_on = models.DateField()

    class Meta:
        ordering = ['year', 'name']
        unique_together = ['name', 'year']

    def __unicode__(self):
        return '{0} {1}'.format(self.name, self.year)


class Holiday(models.Model):
    """Range of days off within a semester. Can be a single day (begin and end are the same
    date) or multiple consecutive days. A semester may have multiple holidays.
    """
    name = models.CharField(max_length=30)
    begin_on = models.DateField()
    end_on = models.DateField()
    semester = models.ForeignKey(Semester, related_name='holidays')

    class Meta:
        ordering = [ 'begin_on' ]

    def includes(self, date):
        """Does date fall on in this holiday?"""
        return self.begin_on <= date <= self.end_on

    def __unicode__(self):
        return self.name


class Building(StampedModel):
    """Campus building."""
    abbrev = models.CharField(max_length=20)
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name


class Room(StampedModel):
    """Room within a building."""
    number = models.CharField(max_length=20)
    building = models.ForeignKey(Building, related_name='rooms')

    def __unicode__(self):
        return '{0} {1}'.format(self.building, self.number)


class Subject(StampedModel):
    """Subject areas such as COS, PHY, SYS, etc. Note that subject and department are not the
    same thing. A department usually offers courses in multiple subjects.
    """
    department = models.ForeignKey(Department, related_name='subjects', blank = True, null = True)
    abbrev = models.CharField(max_length=10) # EG: COS, SYS
    name = models.CharField(max_length=80)   # EG: Computer Science, Systems

    def __unicode__(self):
        return self.abbrev

    class Meta:
        ordering = ['abbrev',]


class CourseAttribute(StampedModel):
    """Course attribute such as SP or CC."""
    abbrev = models.CharField(max_length=10)
    name = models.CharField(max_length=80)

    def __unicode__(self):
        return self.name


AuditInfo = namedtuple("AuditInfo", "requirement, is_satisfied, courses_meeting_reqs")
ReqCO = namedtuple("ReqCO", "required_course, course_offering")

class Constraint(models.Model):
    name = models.CharField(max_length = 80)
    constraint_text = models.CharField(max_length = 100)

    def __unicode__(self):
        return self.name

    def parse_constraint_text(self):
        tokens = self.constraint_text.split()
        name,args = tokens[0],tokens[1:]
        parameters = {}
        for i in range(0, len(args), 2):
            parameters[args[i]] = args[i + 1]
        return (name, parameters)

    def satisfied(self, courseOfferings, requirement):
        name, arguments = self.parse_constraint_text()
        return getattr(self, name)(courseOfferings, requirement, **arguments)

    def courses_meeting_requirement(self, courseOfferings, requirement):
        required_courses = requirement.required_courses()
        co_meeting_reqs = [ReqCO(required_course=required_course, course_offering=co)
                           for required_course in required_courses
                           for co in courseOfferings
                           if co.course == required_course]

        return co_meeting_reqs

    def courses_meeting_all_requirements(self, courseOfferings, requirement):
        required_course = requirement.all_courses()
        co_meeting_reqs = [ReqCO(required_course=required_course, course_offering=co)
                           for required_course in required_course
                           for co in courseOfferings
                           if co.course == required_course]

        return co_meeting_reqs

    def any(self, courses, requirement, **kwargs):
        return len(self.courses_meeting_requirement(courses, requirement)) >= 1

    def all(self, courses, requirement, **kwargs):
        return len(self.courses_meeting_requirement(courses, requirement)) == len(requirement.required_courses())

    def meet_some(self, courses, requirement, **kwargs):
        at_least = int(kwargs['at_least'])
        return len(self.courses_meeting_requirement(courses, requirement)) >= at_least
    
    def min_required_credit_hours (self, courses, requirement, **kwargs):
        at_least = int(kwargs['at_least'])
        return sum(course.credit_hours for course in self.courses_meeting_all_requirements(courses,requirement)) >= at_least

    def all_sub_categories_satisfied(self, courses, requirement, **kwargs):
        sub_categories = requirement.sub_categories()
        satisfied = [sub_category.satisfied(courses) for sub_category in sub_categories]
        return all(satisfied)

    def satisfy_some_sub_categories(self, courses, requirement, **kwargs):
        at_least = int(kwargs['at_least'])
        return len(requirement.satisfied_sub_categories(courses)) >= at_least
    
    def different_departments(self, courses, requirement, **kwargs):
        at_least = int(kwargs['at_least'])
        co_meeting_reqs = self.courses_meeting_all_requirements(courses, requirement)
        courses_meeting_reqs = [reqCo.course_offering.course for reqCo in co_meeting_reqs]
        unique_departments = set(course.subject.abbrev for course in courses_meeting_reqs)
        return len(unique_departments) >= at_least


class Requirement(models.Model):
    name = models.CharField(max_length=50,
                            help_text="e.g., PhysicsBS Technical Electives, or GenEd Literature;"
                            "first part is helpful for searching (when creating a major).")
    
    display_name = models.CharField(max_length=50,
                                    help_text="e.g., Technical Electives, or Literature;"
                                    "this is the title that will show up when students"
                                    "do a graduation audit.")

    constraints = models.ManyToManyField(Constraint, related_name='constraints', blank=True)
    requirements = models.ManyToManyField('self', symmetrical=False, blank=True, related_name = 'sub_requirements')
    courses = models.ManyToManyField('Course', related_name = 'courses', blank=True)

    def __unicode__(self):
        return self.name

    def satisfied_sub_categories(self, courses):
        satisfied_sub_categories = [sub_category 
                                    for sub_category in self.sub_categories()
                                    if sub_category.satisfied(courses)]
        return satisfied_sub_categories


    def required_courses(self):
        return list(self.courses.all())

    def all_courses(self):
        """
        Returns a list of all courses. The courses from Requirement, 
        as well as the courses from sub_requriements.
        """
        reqs = self.requirements.all()
        req_courses = [list(req.all_courses()) for req in reqs]

        return self.required_courses() + (list(chain(*req_courses)))

    def satisfied(self, courses=None):
        courses = [] if courses is None else courses
        return self._satisfied_helper(courses)

    def _satisfied_helper(self, courses):
        satisfied = True
        for constraint in self.constraints.all():
            constraint_satisfied = constraint.satisfied(courses, self)
            satisfied = constraint_satisfied and satisfied 
        return satisfied

    def sub_categories(self):
        return [sub_category for sub_category in self.requirements.all()]

    class Meta:
        ordering = ['display_name', ]


def possible_credit_hours(credit_hour):
    """
    Created for migration. Probably a better way.
    """
    if '-' in credit_hour.value:
        start, end = credit_hour.value.split('-')
        return range(int(start), int(end) + 1)
    elif ',' in credit_hour.value:
        return [int(num) for num in credit_hour.value.split(',')]
    else:
        return [int(credit_hour.value)]

class CreditHour(models.Model):
    name = models.CharField(max_length = 80)
    value = models.CharField(max_length = 20)
    
    def __unicode__(self):
        return self.name


    def valid_credit_hour(self, credit_hour):
        return credit_hour in self.possible_credit_hours

    def possible_credit_hours(self):
        if '-' in self.value:
            start, end = self.value.split('-')
            return range(int(start), int(end) + 1)
        elif ',' in self.value:
            return [int(num) for num in self.value.split(',')]
        else:
            return [int(self.value)]

class Major(models.Model):
    """Academic major"""
    name = models.CharField(max_length=80)
    department = models.ForeignKey(Department, related_name='majors')
    requirement = models.ForeignKey(Requirement, related_name='majors', null=True)

    def __unicode__(self):
        return self.name
     

class Minor(models.Model):
    """Academic minor"""
    name = models.CharField(max_length=80)
    department = models.ForeignKey(Department, related_name='minors')
    requirement = models.ForeignKey(Requirement, related_name='minors', null=True)

    def __unicode__(self):
        return self.name
        

class Course(StampedModel):
    """Course as listed in the catalog."""
    SCHEDULE_YEAR_CHOICES = (('E', 'Even'), ('O', 'Odd'), ('B', 'Both'))

    subject = models.ForeignKey(Subject, related_name='courses')
    number = models.CharField(max_length=10)
    title = models.CharField(max_length=80)
    credit_hours = models.ForeignKey(CreditHour, related_name = 'courses')
    prereqs = models.ManyToManyField('Requirement', blank=True, related_name='prereq_for')
    coreqs  = models.ManyToManyField('Requirement', blank=True, related_name='coreq_for')

    attributes = models.ManyToManyField(CourseAttribute, related_name='courses', blank=True, null=True)

    schedule_semester = models.ManyToManyField(SemesterName, help_text='Semester(s) offered')
    schedule_year = models.CharField(max_length=1, choices=SCHEDULE_YEAR_CHOICES)

    def __unicode__(self):
        return "{0} {1} - {2}".format(self.subject, self.number, self.title)

    def offered_even_years(self):
        return self.schedule_year == 'E' or self.schedule_year == 'B'

    def offered_odd_years(self):
        return self.schedule_year == 'O' or self.schedule_year == 'B'

    def offered_this_year(self, year):
        return ((year % 2 == 0 and self.offered_even_years()) or
                (year % 2 != 0 and self.offered_odd_years()))
                 
    @property
    def department(self):
        return self.subject.department

    class Meta:
        ordering = ['subject', 'number' , 'title']
        unique_together = ('subject', 'number')


class Student(Person):
    university = models.ForeignKey(University, related_name='students')
    student_id = models.CharField(max_length=25)
    entering_year = models.ForeignKey(AcademicYear, related_name='+',
                                      help_text='Year student entered university')
    catalog_year = models.ForeignKey(AcademicYear, related_name='+',
                                     help_text='Catalog year for graduation plan')
    majors = models.ManyToManyField(Major, related_name='students', blank=True, null=True)
    minors = models.ManyToManyField(Minor, related_name='students', blank=True, null=True)

    def __unicode__(self):
        return "{},{}".format(self.student_id, self.first_name, self.last_name)


class CourseOffering(StampedModel):
    """Course as listed in the course schedule (i.e., an offering of a course)."""
    WILL_BE_OFFERED = 0
    NORMALLY_OFFERED_BUT_NOT = 1
    NOT_NORMALLY_OFFERED_BUT_IS = 2
    STATUS_CHOICES = (
        (WILL_BE_OFFERED, 'Will be offered'),
        (NORMALLY_OFFERED_BUT_NOT, 'Normally offered but will not be offered this semester'),
        (NOT_NORMALLY_OFFERED_BUT_IS, 'Not normally offered but will be offered this semester'),
    )

    course = models.ForeignKey(Course, related_name='offerings')
    credit_hours = models.PositiveSmallIntegerField(default=3)
    semester = models.ForeignKey(Semester)
    instructor = models.ManyToManyField(FacultyMember, through='OfferingInstructor',
                                        blank=True, null=True,
                                        related_name='course_offerings')
    status = models.PositiveSmallIntegerField(choices = STATUS_CHOICES, default = WILL_BE_OFFERED)

    def __unicode__(self):
        return "{0} ({1})".format(self.course, self.semester)

    def department(self):
        return self.course.department

    def students(self):
        """Students enrolled in this course offering"""
        return Student.objects.filter(courses_taken=self)

class PlannedCourse(StampedModel):
    """Course that a student is actually planning to take."""
    student = models.ForeignKey(Student, related_name='planned_courses')
    offering = models.ForeignKey(CourseOffering, related_name='+')
    
    def __unicode__(self):
        return "{} {}".format(self.student,self.offering.course)

class Grade(models.Model):
    letter_grade = models.CharField(max_length=5)
    grade_points = models.FloatField()

    def __unicode__(self):
        return self.letter_grade


class CourseTaken(StampedModel):
    student = models.ForeignKey(Student, related_name='courses_taken')
    course_offering = models.ForeignKey(CourseOffering)
    final_grade = models.ForeignKey(Grade, blank=True)


class OfferingInstructor(StampedModel):
    """Relate a course offering to one (of the possibly many) instructors teaching the
    course. The primary purpose for this model is to track load credit being granted to
    each instructor of the course.
    """
    course_offering = models.ForeignKey(CourseOffering)
    instructor = models.ForeignKey(FacultyMember)
    load_credit = models.FloatField()


class ClassMeeting(StampedModel):
    """A single meeting of a class, which takes place on a given day, in a period of clock
    time, in a certain room, and led by a single instructor. This model allows
    considerable flexibility as to who teaches each meeting of a course. It also provides
    a hook where we can track content for each meeting of the course.
    """
    held_on = models.DateField()
    begin_at = models.TimeField()
    end_at = models.TimeField()
    course_offering = models.ForeignKey(CourseOffering, related_name='class_meetings')
    room = models.ForeignKey(Room)
    instructor = models.ForeignKey(FacultyMember)

    def __unicode__(self):
        return '{0} ({1} {2})'.format(self.course_offering, self.held_on, self.begin_at)













