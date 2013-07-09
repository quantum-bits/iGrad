from common_models import *
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from grad_audit import MetCourse, GradAudit
import datetime
from collections import defaultdict, OrderedDict
import itertools

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

    def audit(self, courseOfferings, requirement):
        name, arguments = self.parse_constraint_text()
        return getattr(self, name)(courseOfferings, requirement, **arguments)

            
    def met_courses(self, courseOfferings, requirement, getCourses):
        required_courses = getCourses()
        met_courses = [MetCourse(required_course=required_course, course_offering=co)
                       for required_course in required_courses
                       for co in courseOfferings
                       if co.course == required_course]
        return met_courses

    def courses_meeting_requirement(self, courseOfferings, requirement):
        required_courses = requirement.required_courses()
        met_courses = [MetCourses(required_course=required_course, course_offering=co)
                       for required_course in required_courses
                       for co in courseOfferings
                       if co.course == required_course]

        return met_courses

    def courses_meeting_all_requirements(self, courseOfferings, requirement):
        required_course = requirement.all_courses()
        co_meeting_reqs = [ReqCO(required_course=required_course, course_offering=co)
                           for required_course in required_course
                           for co in courseOfferings
                           if co.course == required_course]

        return co_meeting_reqs

    def any(self, courses, requirement, **kwargs):
        met_courses = self.met_courses(courses, requirement, requirement.required_courses)
        is_satisfied = len(met_courses) >= 1
        return GradAudit(requirement=requirement, is_satisfied=is_satisfied, met_courses=met_courses)


    def all(self, courses, requirement, **kwargs):
        met_courses = self.met_courses(courses, requirement, requirement.required_courses)
        is_satisfied = len(met_courses) == len(requirement.required_courses())
        return GradAudit(requirement=requirement, is_satisfied=is_satisfied, met_courses=met_courses)


    def meet_some(self, courses, requirement, **kwargs):
        at_least = int(kwargs['at_least'])
        met_courses = self.met_courses(courses, requirement, requirement.required_courses)
        is_satisfied = len(met_courses) >= at_least
        return GradAudit(requirement=requirement, met_courses=met_courses, is_satisfied=is_satisfied)
    
    def min_required_credit_hours (self, courses, requirement, **kwargs):
        at_least = int(kwargs['at_least'])

        course_offerings = [] 
        courses_considered = [] 
        met_courses = self.met_courses(courses, requirement, requirement.all_courses)
        for met_course in met_courses:
            course_offering = met_course.course_offering
            course = course_offering.course
            if course_offering.course not in courses_considered:
                # if a person takes a course multiple times, it should only count once.
                course_offerings.append(course_offering)
                courses_considered.append(course_offering.course)

        is_satisfied = sum(co.credit_hours for co in course_offerings) >= at_least
        return GradAudit(requirement=requirement, is_satisfied=is_satisfied, met_courses=met_courses)

    def different_departments(self, courses, requirement, **kwargs):
        at_least = int(kwargs['at_least'])
        met_courses = self.met_courses(courses, requirement, requirement.all_courses)
        courses = [met_course.required_course for met_course in met_courses]
        unique_departments = set(course.subject.abbrev for course in courses)
        is_satisfied = len(unique_departments) >= at_least
        return GradAudit(requirement=requirement, met_courses=met_courses, is_satisfied=is_satisfied)

    def all_sub_requirements_satisfied(self, courses, requirement, **kwargs):
        grad_audits = [child.audit(courses) for child in requirement.child_requirements()]
        is_satisfied = all([grad_audit.is_satisfied for grad_audit in grad_audits])
        grad_audit = GradAudit(requirement=requirement, met_course=None, is_satisfied=is_satisfied)
        grad_audit.addChildren(*grad_audits)
        return grad_audit

    def satisfy_some_sub_requirements(self, courses, requirement, **kwargs):
        at_least = int(kwargs['at_least'])
        grad_audits = [child.audit(courses) for child in requirement.child_requirements()]
        satisfied_grad_audits = [grad_audit for grad_audit in grad_audits if grad_audit.is_satisfied]
        is_satisfied = len(satisfied_grad_audits) >= at_least
        grad_audit = GradAudit(requirement=requirement, is_satisfied=is_satisfied, met_course=None)
        grad_audit.addChildren(*grad_audits)
        return grad_audit
    

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

    def satisfied(self, offerings):
        return self.audit(offerings).is_satisfied
        
    def satisfied_grad_audits(self, courses):
        satisfied_grad_audits = []
        for child_requirement in self.child_requirements():
            grad_audit = child_requirement.audit(courses)
            print '\n'.join(str(ga) for ga in grad_audit)
            if grad_audits_satisfied(grad_audit):
                satisfied_grad_audits.append(grad_audit)
            
        return satisfied_grad_audits

    def required_courses(self):
        return list(self.courses.all())

    def all_courses(self):
        """
        Returns a list of all courses. The courses from Requirement, 
        as well as the courses from sub_requriements.
        """
        reqs = self.requirements.all()
        req_courses = [list(req.all_courses()) for req in reqs]

        return self.required_courses() + (list(itertools.chain(*req_courses)))

    def audit(self, courses=None):
        """Returns a list of AuditInfos for each constraint on this requirement.
        """
        courses = [] if courses is None else courses
        return self._audit_helper(courses)

    def _audit_helper(self, courses):
        children =  [constraint.audit(courses, self) for constraint in self.constraints.all()]
        is_satisfied = all([child.is_satisfied for child in children])
        gradAudit = GradAudit(requirement=self, met_courses=None, is_satisfied=is_satisfied)
        gradAudit.addChildren(*children)
        return gradAudit

    def child_requirements(self):
        return [child_requirement for child_requirement in self.requirements.all()]

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

    @property
    def abbrev_name(self):
        return "{} {}".format(self.subject.abbrev, self.number)
    
    @property
    def is_sp(self):
        return bool(self.attributes.filter(course=self, abbrev='SP'))
    
    @property
    def is_cc(self):
        return bool(self.attributes.filter(course=self, abbrev='CC'))

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

    def has_major(self):
        return len(self.majors.all()) > 0

    def offerings_this_semester(self, semester):
        offerings = [pc.offering for pc in self.planned_courses.all() if pc.offering.semester == semester]
        return offerings

    def credit_hours_this_semester(self, semester):
        return sum(course.credit_hours 
                   for course in self.offerings_this_semester(semester))

    def credit_hours_in_plan(self):
        credit_hours = 0
        for course in self.planned_courses.all():
            credit_hours += course.credit_hours

        for course_substitution in self.course_substitutions.all():
            credit_hours += course_substitutions.credit_hours

        return credit_hours

    def four_year_plan(self):
        plan = []
        for year in self.entering_year.next_five_years():
            year_plan = {}
            credit_hours = []
            year_semesters = OrderedDict()
            for semester in year.semesters.all():
                semester_courses = {}
                offerings = self.offerings_this_semester(semester)
                for offering in offerings:
                    course = {}
                    course['title'] = offering.course.title
                    course['number'] = offering.course.abbrev
                    course['credit_hours'] = offering.credit_hours
                    course['sp'] = offering.course.is_sp
                    course['cc'] = offering.course.is_cc
                    course['other_semesters_offered'] = offering.other_offerings()
                    other_semesters = [{'id' : semester.id, 
                                        'credit_hours' : self.credit_hours_this_semester(semester)}
                                       for semester in offering.other_offerings()]
                    course['id'] = offering.course.id
                    semester_courses.append(course)

                year_semesters[semester] = semester_courses
                credit_hours.append(self.credit_hours_this_semester(semester))

            year_plan['semesters'] = year_semesters
            year_plan['credit_hours'] = credit_hours
            plan.append(year_plan)
        return plan



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

    def other_offerings(self):
        """Returns a list of other semesters this course is 
        offered.
        """
        course = self.course
        offerings = [offering.semester for offering in self.objects.filter(course=course).exclude(courseOffering)]
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













