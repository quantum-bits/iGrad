from collections import defaultdict
from collections import namedtuple
from common_models import *
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum
from django.db.models.signals import post_save
from django.dispatch import receiver
import datetime

import logging
logger = logging.getLogger(__name__)


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

    def next_five_years(self):
        """Returns the next five academic years.
        starting with this one.
        """
        first_year = self.begin_on.year
        yield self
        for year in range(first_year + 1, first_year + 5):
            yield AcademicYear.objects.get(begin_on__year = year)
        
    def __unicode__(self):
        return '{0}-{1}'.format(self.begin_on.year, self.end_on.year)


    def actual_year(self, semesterName):
        if semesterName.fall:
            year = self.begin_on.year
        else:
            year = self.end_on.year
        return year

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


class SemesterDateDefault(models.Model):
    """Model for representing default dates given an SemesterName
    such as. August 1 for fall, and January 2 for J-Term. """
    MONTH_CHOICES = ((1,  'January'),
                     (2,  'February'),
                     (3,  'March'),
                     (4,  'April'),
                     (5,  'May'),
                     (6,  'June'),
                     (7,  'July'),
                     (8,  'August'),
                     (9,  'September'),
                     (10, 'October'),
                     (11, 'November'),
                     (12, 'December'))

    name = models.OneToOneField(SemesterName)
    begin_month = models.PositiveSmallIntegerField(choices=MONTH_CHOICES)
    begin_day   = models.PositiveSmallIntegerField()
    end_month   = models.PositiveSmallIntegerField(choices=MONTH_CHOICES)
    end_day     = models.PositiveSmallIntegerField()


    def begin_on(self, year):
        return datetime.date(year.actual_year(self.name), self.begin_month, self.begin_day)
    def end_on(self, year):
        return datetime.date(year.actual_year(self.name), self.end_month, self.end_day)
    def __unicode__(self):
        return "{} Defaults".format(self.name)

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

@receiver(post_save, sender=AcademicYear)
def create_semesters(sender, **kwargs):
    """Creates semesters for an AcademicYear when a new academic year is created."""
    instance = kwargs['instance']
    created  = kwargs['created']
    raw      = kwargs['raw']
    if created and not raw:
        for semesterName in SemesterName.objects.all():
            begin_on = semesterName.semesterdatedefault.begin_on(instance)
            end_on   = semesterName.semesterdatedefault.end_on(instance)
            semester, created = Semester.objects.get_or_create(name=semesterName,year=instance,
                                                               begin_on = begin_on, end_on=end_on)
    
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

    @property
    def max_credit_hour(self):
        return max(self.possible_credit_hours())

    @property
    def min_credit_hour(self):
        return min(self.possible_credit_hours())

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
    requirement = models.OneToOneField('Requirement', related_name='major', null=True)

    def __unicode__(self):
        return self.name
     

class Minor(models.Model):
    """Academic minor"""
    name = models.CharField(max_length=80)
    department = models.ForeignKey(Department, related_name='minors')
    requirement = models.OneToOneField('Requirement', related_name='minor', null=True)

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

    @property
    def abbrev(self):
        return "{} {}".format(self.subject.abbrev, self.number)
    
    @property
    def is_sp(self):
        return bool(self.attributes.filter(abbrev='SP'))
    
    @property
    def is_cc(self):
        return bool(self.attributes.filter(abbrev='CC'))

    @property 
    def possible_credit_hours(self):
        return ",".join(str(i) for i in self.credit_hours.possible_credit_hours())

    def __unicode__(self):
        return "{0} {1} - {2}".format(self.subject, self.number, self.title)

    def offered_even_years(self):
        return self.schedule_year == 'E' or self.schedule_year == 'B'

    def offered_odd_years(self):
        return self.schedule_year == 'O' or self.schedule_year == 'B'

    def offered_this_year(self, year):
        return ((year % 2 == 0 and self.offered_even_years()) or
                (year % 2 != 0 and self.offered_odd_years()))

    def prereqs_satisfied(self, offerings):
        return all([prereq.satisfied(offerings) for prereq in self.prereqs])
    
    def coreqs_satisfied(self, offerings):
        return all([coreq.satisfied(offerings) for coreq in self.coreqs])

    @property
    def department(self):
        return self.subject.department

    class Meta:
        ordering = ['subject', 'number' , 'title']
        unique_together = ('subject', 'number')

class UserProxy(User):
    class Meta:
        proxy = True

    def __unicode__(self):
        return self.get_full_name()

    def is_student(self):
        try:
            if self.student:
                return True
        except Student.DoesNotExist:
            return False

    def is_professor(self):
        try:
            if self.professor:
                return True
        except Professor.DoesNotExist:
            return False

    def get_student_id(self):
        assert(self.is_student)
        return self.student.id

    def get_professor_id(self):
        assert(self.is_professor)
        return self.professor.id


class ProxiedModelBackend(ModelBackend):
    def get_user(self, user_id):
        try:
            return UserProxy.objects.get(pk=user_id)
        except UserProxy.DoesNotExist:
            return None


class Student(Person):
    user = models.OneToOneField(User, null=True)
    university = models.ForeignKey(University, related_name='students')
    student_id = models.CharField(max_length=25)
    entering_year = models.ForeignKey(AcademicYear, related_name='+',
                                      help_text='Year student entered university')
    catalog_year = models.ForeignKey(AcademicYear, related_name='+',
                                     help_text='Catalog year for graduation plan')
    majors = models.ManyToManyField(Major, related_name='students', blank=True, null=True)
    minors = models.ManyToManyField(Minor, related_name='students', blank=True, null=True)

    planned_courses = models.ManyToManyField('CourseOffering', related_name='students', blank=True, null=True)


    def __unicode__(self):
        return "{},{}".format(self.student_id, self.first_name, self.last_name)

    def yearName(self, semester):
        year_index = 0
        years = ["Freshman", "Sophomore", "Junior", "Senior", "Super Senior"]
        for year in self.entering_year.next_five_years():
            if semester.year == year:
                return years[year_index]
            year_index += 1

        return "Super Senior"

    def has_major(self):
        return len(self.majors.all()) > 0

    def planned_courses_before_semester(semester):
        return self.planned_courses.filter(semester__end_on__lt=semester.begin_on)

    def offerings_this_semester(self, semester):
        return self.planned_courses.filter(semester=semester)

    def credit_hours_this_semester(self, semester):
        credit_hours = self.offerings_this_semester(semester).aggregate(Sum('credit_hours'))['credit_hours__sum']
        if credit_hours is None: return 0
        return credit_hours

    def credit_hours_in_plan(self):
        planned_course_chs = self.planned_courses.all().aggregate(Sum('credit_hours'))['credit_hours__sum']
        if planned_course_chs is None: planned_course_chs = 0
        course_sub_chs = self.course_substitutions.all().aggregate(Sum('credit_hours'))['credit_hours__sum']
        if course_sub_chs is None: course_sub_chs = 0
        return planned_course_chs + course_sub_chs
    
    def four_year_plan(self):
        SemesterInfo = namedtuple('SemesterInfo','courses, semester')
        plan = []
        for year in self.entering_year.next_five_years():
            year_plan = {}
            credit_hours = []
            year_semesters = []
            for semester in year.semesters.all():
                semester_courses = []
                offerings = self.offerings_this_semester(semester)
                for offering in offerings:
                    course = {}
                    course['title'] = offering.course.title
                    course['number'] = offering.course.abbrev
                    course['credit_hours'] = offering.credit_hours
                    course['sp'] = offering.course.is_sp
                    course['cc'] = offering.course.is_cc
                    course['other_semesters_offered'] = []
                    for other_offering in CourseOffering.other_offerings(offering):
                        course['other_semesters_offered'].append({'id' : other_offering.id, 
                                                                  'semester' : other_offering.semester, 
                                                                  'credit_hours' : self.credit_hours_this_semester(other_offering.semester)})

                    
                    course['id'] = offering.id
                    semester_courses.append(course)
                year_semesters.append(SemesterInfo(courses=semester_courses, semester=semester))
                credit_hours.append(self.credit_hours_this_semester(semester))
            year_plan['semesters'] = year_semesters
            year_plan['credit_hours'] = credit_hours
            plan.append(year_plan)
        return plan

    def sp_cc_information(self):
        all_courses = self.planned_courses.all()
        sps = [course for course in all_courses if course.course.is_sp]
        ccs = [course for course in all_courses if course.course.is_cc]
        num_sps = len(sps)
        num_ccs = len(ccs)
        
        return {'sps' : sps, 
                'num_sps' : num_sps,
                'sps_met' : num_sps >= 2,
                'ccs' : ccs,
                'num_ccs' : num_ccs,
                'ccs_met' : num_ccs >=1}

    def courses_covered(self):
        """
        Returns a dictionary where the key is the course that is being met, 
        and the value is the course offering/ substitute/ transfer that meets it.
        """
        # TODO add suport for substitution courses
        result = {}
        for course_offering in self.planned_courses.all():
            result[course_offering.course] = course_offering
        return result
        
    def grad_audit(self):
        # Right now it returns the first major,
        # TODO: make it work when there is more than one major. 
        # TODO: make it work for minors
        for major in self.majors.all():
            return major.requirement.audit(self.planned_courses.all())

class Professor(Person):
    user = models.OneToOneField(User, null=True)
    advisee = models.OneToOneField(Student, null=True, blank=True)

    def __unicode__(self):
        return "{} {}".format(self.first_name, self.last_name)


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

    def prereqs(self):
        return self.course.prereqs.all()
    
    def coreqs(self):
        return self.course.coreqs.all()


    @classmethod
    def other_offerings(cls,offering):
        """Returns a list of other semesters this course is 
        offered.
        """
        offerings = cls.objects.filter(course=offering.course)
        offerings = offerings.exclude(semester=offering.semester)
        return offerings

    def __unicode__(self):
        return "{0} ({1})".format(self.course, self.semester)

    def department(self):
        return self.course.department



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













