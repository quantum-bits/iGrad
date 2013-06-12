from common_models import *
from django.db import models
from itertools import chain

import logging
logger = logging.getLogger(__name__)
LOG_FILENAME = 'constraint.log'
logging.basicConfig(filename=LOG_FILENAME, level = logging.DEBUG, filemode = 'w')


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


class Major(models.Model):
    """Academic major"""
    name = models.CharField(max_length=80)
    department = models.ForeignKey(Department, related_name='majors')

    def __unicode__(self):
        return self.name
        

class Minor(models.Model):
    """Academic minor"""
    name = models.CharField(max_length=80)
    department = models.ForeignKey(Department, related_name='minors')

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
    begin_on = models.DateField()
    end_on = models.DateField()

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
    department = models.ForeignKey(Department, related_name='subjects')
    abbrev = models.CharField(max_length=10) # EG: COS, SYS
    name = models.CharField(max_length=80)   # EG: Computer Science, Systems

    def __unicode__(self):
        return self.abbrev


class CourseAttribute(StampedModel):
    """Course attribute such as SP or CC."""
    abbrev = models.CharField(max_length=10)
    name = models.CharField(max_length=80)

    def __unicode__(self):
        return self.name


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

    def satisfied(self, courses, requirement):
        name, arguments = self.parse_constraint_text()
        return getattr(self, name)(courses, requirement, **arguments)

    def any(self, courses, requirement, **kwargs):
        required_courses = requirement.all_courses()
        common_courses = set(required_courses).intersection(set(courses))
        return len(common_courses) >= 1

    def all(self, courses, requirement, **kwargs):
        required_courses = requirement.all_courses()
        un_met_courses = set(required_courses) - set(courses)
        return un_met_courses == 0

    def meet_some(self, courses, requirement, **kwargs):
        required_courses = requirement.all_courses()
        met_courses = set(required_courses).intersection(set(courses))
        at_least = int(kwargs['at_least'])
        return len(met_courses) >= at_least
    
    def min_required_credit_hours (self, courses, requirement, **kwargs):
        at_least = int(kwargs['at_least'])
        all_courses = requirement.all_courses()
        courses_meeting_reqs = set(all_courses).intersection(set(courses))
        return sum(course.credit_hours for course in courses_meeting_reqs) >= at_least

    def all_sub_categories_satisfied(self, courses, requirement, **kwargs):
        sub_categories = requirement.sub_categories()
        satisfied = [sub_category.satisfied(*courses) for sub_category in sub_categories]
        return all(satisfied)

    def satisfy_some_sub_categories(self, courses, requirement, **kwargs):
        at_least = int(kwargs['at_least'])
        return len(requirement.satisfied_sub_categories(courses)) >= at_least
        
        
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
                                    if sub_category.satisfied(*courses)]
        return satisfied_sub_categories

    def all_courses(self):
        courses = self.courses.all()
        reqs = self.requirements.all()
        req_courses = [list(req.all_courses()) for req in reqs]

        return list(courses) + (list(chain(*req_courses)))

    def satisfied(self, *courses):
        satisfied = True
        for constraint in self.constraints.all():
            constraint_satisfied = constraint.satisfied(courses, self)
            if not constraint_satisfied:
                logging.debug('{}: {} not satisfied'.format(self, constraint.name))
            satisfied = constraint_satisfied and satisfied 
        return satisfied

    def sub_categories(self):
        return [sub_category for sub_category in self.requirements.all()]


class Course(StampedModel):
    """Course as listed in the catalog."""
    SCHEDULE_YEAR_CHOICES = (('E', 'Even'), ('O', 'Odd'), ('B', 'Both'))

    subject = models.ForeignKey(Subject, related_name='courses')
    number = models.CharField(max_length=10)
    title = models.CharField(max_length=80)
    credit_hours = models.PositiveIntegerField(default=3)
    prereqs = models.ManyToManyField('Requirement', blank=True, related_name='prereq_for')
    coreqs  = models.ManyToManyField('Requirement', blank=True, related_name='coreq_for')

    attributes = models.ManyToManyField(CourseAttribute, related_name='courses', blank=True, null=True)

    schedule_semester = models.ManyToManyField(SemesterName, help_text='Semester(s) offered')
    schedule_year = models.CharField(max_length=1, choices=SCHEDULE_YEAR_CHOICES)

    def __unicode__(self):
        return "{0} {1} - {2}".format(self.subject, self.number, self.title)

    @property
    def department(self):
        return self.subject.department

    class Meta:
        ordering = ['subject', 'number' , 'title']


class Student(Person):
    university = models.ForeignKey(University, related_name='students')
    student_id = models.CharField(max_length=25)
    entering_year = models.ForeignKey(AcademicYear, related_name='+',
                                      help_text='Year student entered university')
    catalog_year = models.ForeignKey(AcademicYear, related_name='+',
                                     help_text='Catalog year for graduation plan')
    majors = models.ManyToManyField(Major, related_name='students', blank=True, null=True)
    minors = models.ManyToManyField(Minor, related_name='students', blank=True, null=True)


class CourseOffering(StampedModel):
    """Course as listed in the course schedule (i.e., an offering of a course)."""
    course = models.ForeignKey(Course, related_name='offerings')
    semester = models.ForeignKey(Semester)
    instructor = models.ManyToManyField(FacultyMember, through='OfferingInstructor',
                                        blank=True, null=True,
                                        related_name='course_offerings')

    def __unicode__(self):
        return "{0} ({1})".format(self.course, self.semester)

    def department(self):
        return self.course.department

    def students(self):
        """Students enrolled in this course offering"""
        return Student.objects.filter(courses_taken=self)


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












