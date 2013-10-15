from collections import defaultdict
from collections import namedtuple
from collections import deque
from common_models import *
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum
from django.db.models.signals import post_save
from django.dispatch import receiver
import datetime
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

    def __cmp__(self, other):
        if self.seq < other.seq: return -1
        if self.seq > other.seq: return 1
        if self.seq == other.seq: return 0

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

    def __cmp__(self, other):
        if self.year < other.year: return -1
        if self.year > other.year: return 1
        return self.name.__cmp__(other.name)


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
    catalog_year = models.ForeignKey(AcademicYear, related_name='majors', null=True)

    def __unicode__(self):
        return "{} {}".format(self.name, self.catalog_year)
     

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
    graduationRequirement = models.OneToOneField('Requirement', blank=True, null=True)


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

    def candidate_courses(self, **kwargs):
        """
        Returns an iterable containing courseOfferings and courseSubstitutions
        that a student plans to take, that may meet course requirement.
        kwargs: before, during, after. 
        Each argument can be used to filter the list with a semester. 
        """
        result = list(itertools.chain(self.planned_courses.all(), self.course_substitutions.all()))

        before =  kwargs.get('before', None)
        if before is not None:
            result = filter(lambda c: c.semester < before, result)

        during = kwargs.get('during', None)
        if during is not None:
            result = filter(lambda c: c.semester == during, result)
        
        after = kwargs.get('after', None)
        if after is not None:
            result = filter(lambda c: c.semester > after, result)
        
        return result


    def credit_hours_this_semester(self, semester):
        return sum([c.credit_hours for c in self.candidate_courses(during=semester)])

    def credit_hours_in_plan(self):
        planned_course_chs = self.planned_courses.all().aggregate(Sum('credit_hours'))['credit_hours__sum']
        if planned_course_chs is None: planned_course_chs = 0
        course_sub_chs = self.course_substitutions.all().aggregate(Sum('credit_hours'))['credit_hours__sum']
        if course_sub_chs is None: course_sub_chs = 0
        return sum([c.credit_hours for c in self.candidate_courses()])
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
                offerings = self.candidate_courses(during=semester)
                for offering in offerings:
                    course = {}
                    course['title'] = offering.course.title
                    course['number'] = offering.course.abbrev
                    course['credit_hours'] = offering.credit_hours
                    course['sp'] = offering.course.is_sp
                    course['cc'] = offering.course.is_cc
                    course['other_semesters_offered'] = []
                    for other_offering in offering.other_offerings():
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

    def grad_audit(self):
        req = Requirement.make_graduation_requirement(self)
        return req.audit(self.candidate_courses(), student=self)

@receiver(post_save, sender=Student)
def setUp_graduationPlan(sender, **kwargs):
    instance = kwargs['instance']
    created = kwargs['created']
    raw = kwargs['raw']
    if created and not raw:
        Requirement.make_graduation_requirement(instance)
        

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

     def other_offerings(self):
         offerings = CourseOffering.objects.filter(course=self.course)
         offerings = offerings.exclude(semester=self.semester)
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


class CourseSubType(models.Model):
    """Model for determining what type of substitution. Transfer, Sub, Etc."""
    name = models.CharField(max_length=80, unique=True)

    def __unicode__(self):
         return self.name

    @property
    def is_transfer(self):
         return self.name == 'Transfer'

    @property
    def is_sub(self):
         return self.name == 'Subsitution'


class CourseSubstitution(models.Model):
    """Course transferred from another institution."""
    university = models.ForeignKey(University, related_name='course_substitutions',
                                   blank=True, null=True)
    title = models.CharField(max_length=80)
    credit_hours = models.PositiveIntegerField(default=3)
    semester = models.ForeignKey(Semester, blank=True, null=True)
    equivalent_course = models.ForeignKey(Course, related_name='course_substitutions')
    student = models.ForeignKey(Student, related_name='course_substitutions')
    sub_type = models.ForeignKey(CourseSubType, related_name='course_substitutions', null=True, blank=True)

    @property
    def is_sp(self): return self.equivalent_course.is_sp
    @property
    def is_cc(self): return self.equivalent_course.is_cc
    
    @property
    def course(self):
        return self.equivalent_course 

    def other_offerings(self): return []

    def is_transfer(self):
        self.sub_type.is_transfer

    def is_sub(self):
        self.sub_type.is_sub

    def __unicode__(self):
        return self.title

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





def is_substitution(course):
    return type(course) == CourseSubstitution

class GradAudit(object):
    def __init__(self, **kwargs):
        self.requirement = kwargs.get('requirement')
        self.met_courses = kwargs.get('met_courses', {})
        self.is_satisfied = kwargs.get('is_satisfied')
        self.constraint_messages = kwargs.get('constraint_messages', [])
        self.children = kwargs.get('children', [])
        self.unused_courses = kwargs.get('unused_courses', None)
        self.student = kwargs.get('student', None)

    def addMessage(self, msg):
        self.constraint_messages.append(msg)

    def addChild(self, child):
        self.children.append(child)
        self.addMetCourses(child.met_courses)

    def addChildren(self, *children):
        for child in children:
            self.addChild(child)
    
    def addMetCourse(self, met_course, course_offering):
        self.met_courses[met_course] = course_offering
    
    def addMetCourses(self, met_courses):
        for met_course, course_offering in met_courses.items():
            self.addMetCourse(met_course, course_offering)

    def __iter__(self):
        self._stack = deque([])
        self._stack.append(self)
        return self
    
    def next(self):
        if not self._stack:
            raise StopIteration

        audit = self._stack.pop()
        for child in audit.children:
            self._stack.append(child)
        return audit


class GradAuditTemplate(object):
    def __init__(self, audit):
        self.audit = audit
        self.student = audit.student

    def semesterDescription(self, semester):
        yearName = self.audit.student.yearName(semester)
        semester_name = semester.name
        year = semester.begin_on.year
        return '{} {} ({})'.format(yearName, semester_name, year)

    def courseInfo(self, required_course):
        info = {}
        info['course_id'] = required_course.id
        info['title'] = required_course.title
        info['abbrev'] = required_course.abbrev
        info['credit_hours'] = required_course.possible_credit_hours
        info['sp'] = required_course.is_sp
        info['cc'] = required_course.is_cc
        if required_course in self.audit.met_courses:
            courseOffering = self.audit.met_courses[required_course]
            info['is_sub'] = is_substitution(courseOffering)
            yearName = self.audit.student.yearName(courseOffering.semester)
            semester_name = courseOffering.semester.name
            year = courseOffering.semester.begin_on.year
            info['met'] = True
            info['offering_id'] = courseOffering.id
            info['taken_for'] = courseOffering.credit_hours
            info['hours_match'] = courseOffering.credit_hours == required_course.credit_hours.min_credit_hour
            info['comment'] = self.semesterDescription(courseOffering.semester)

            info['other_semesters'] = []
            for offering in courseOffering.other_offerings():
                info['other_semesters'].append({'course_id' : offering.id,
                                                'semester'  : offering.semester, 
                                                'hours_this_semester' : self.student.credit_hours_this_semester(offering.semester)})


        else:
            info['comment'] = None
            info['met'] = False
            info['other_semesters'] = []
            for offering in CourseOffering.objects.filter(course=required_course):
                info['other_semesters'].append({'course_id' : offering.id,
                                                'semester'  : offering.semester, 
                                                'hours_this_semester' : self.student.credit_hours_this_semester(offering.semester)})
        return info

    def requirementBlock(self, audit):
        """Creates requirement block information to be used directly
        in gradaudit.html template."""
        
        requirement = audit.requirement
        block = {}
        block['name'] = requirement.name
        block['min_required_credit_hours'] = requirement.min_required_credit_hours
        block['constraint_comments'] = audit.constraint_messages
        block['courses'] = []
        block['comments'] = []
        
        for course in requirement.required_courses():
            block['courses'].append(self.courseInfo(course))

        
        return block

    def requirementBlocks(self):
        """Returns requirementBlocks produced from each grad_audit."""
        return [self.requirementBlock(grad_audit) for grad_audit in self.audit]



class Constraint(models.Model):
    name = models.CharField(max_length = 80)
    constraint_text = models.CharField(max_length = 100)
    comment = models.CharField(max_length = 200, null=True, blank=True)

    def __unicode__(self):
        return self.name

    def parse_constraint_text(self):
        tokens = self.constraint_text.split()
        name,args = tokens[0],tokens[1:]
        parameters = {}
        for i in range(0, len(args), 2):
            parameters[args[i]] = args[i + 1]
        return (name, parameters)

    def remove_met_courses_from_unused_courses(self, met_courses, unused_courses):
        met_courses = met_courses.values()
        return unused_courses - set(met_courses)

    def audit(self, courseOfferings, requirement, unused_courses):
        name, arguments = self.parse_constraint_text()
        return getattr(self, name)(courseOfferings, requirement, unused_courses,**arguments)

    def any(self, courses, requirement, unused_courses, **kwargs):
        met_courses = requirement.met_courses(courses)
        unused_courses = self.remove_met_courses_from_unused_courses(met_courses, unused_courses)
        is_satisfied = len(met_courses) >= 1
        return GradAudit(requirement=requirement, is_satisfied=is_satisfied, met_courses=met_courses), unused_courses


    def all(self, courses, requirement, unused_courses, **kwargs):
        met_courses = requirement.met_courses(courses)
        unused_courses = self.remove_met_courses_from_unused_courses(met_courses, unused_courses)
        is_satisfied = len(met_courses) == len(requirement.required_courses())
        return GradAudit(requirement=requirement, is_satisfied=is_satisfied, met_courses=met_courses), unused_courses


    def meet_some(self, courses, requirement, unused_courses, **kwargs):
        at_least = int(kwargs['at_least'])
        met_courses = requirement.met_courses(courses)
        unused_courses = self.remove_met_courses_from_unused_courses(met_courses, unused_courses)        
        is_satisfied = len(met_courses) >= at_least
        return GradAudit(requirement=requirement, met_courses=met_courses, is_satisfied=is_satisfied), unused_courses
    

    def min_required_credit_hours (self, courses, requirement, unused_courses, **kwargs):
        at_least = int(kwargs['at_least'])
        course_offerings = [] 
        courses_considered = [] 
        met_courses = requirement.met_courses(courses, True)
        unused_courses = self.remove_met_courses_from_unused_courses(met_courses, unused_courses)
        def course_has_been_considered(course):
            return course in courses_considered

        for met_course in met_courses:
            course_offering = met_courses[met_course]
            course = course_offering.course
            if not course_has_been_considered(course):
                course_offerings.append(course_offering)
                courses_considered.append(course_offering.course)
        
        print ("\n".join(str(co) for co in course_offerings))
        is_satisfied = sum(co.credit_hours for co in course_offerings) >= at_least
        return GradAudit(requirement=requirement, is_satisfied=is_satisfied, met_courses=met_courses), unused_courses

    def different_departments(self, courses, requirement, unused_courses, **kwargs):
        at_least = int(kwargs['at_least'])
        met_courses = requirement.met_courses(courses, True)
        unused_courses = self.remove_met_courses_from_unused_courses(met_courses, unused_courses)
        courses = [met_course for met_course in met_courses]
        # TODO: Change this. The heuristic is that if a course has different abbreviations
        # it is from different departments. This is not always the case.
        unique_departments = set(course.subject.abbrev for course in courses)
        is_satisfied = len(unique_departments) >= at_least
        return GradAudit(requirement=requirement, met_courses=met_courses, is_satisfied=is_satisfied), unused_courses

    def sub_requirements_grad_audits(self, courses, requirement, unused_courses):
        """Returns a collection of grad audits, unused_courses."""
        grad_audits = []
        for child in requirement.child_requirements():
            grad_audit, unused_courses = child.audit(courses, unused_courses)
            grad_audits.append(grad_audit)
        return grad_audits, unused_courses 

    def all_sub_requirements_satisfied(self, courses, requirement, unused_courses, **kwargs):
        grad_audits, unused_courses = self.sub_requirements_grad_audits(courses, requirement, unused_courses)
        is_satisfied = all([grad_audit.is_satisfied for grad_audit in grad_audits])
        grad_audit = GradAudit(requirement=requirement, is_satisfied=is_satisfied, children=grad_audits)
        return grad_audit, unused_courses

    def satisfy_some_sub_requirements(self, courses, requirement, unused_courses, **kwargs):
        at_least = int(kwargs['at_least'])
        grad_audits, unused_courses = self.sub_requirements_grad_audits(courses, requirement, unused_courses)
        satisfied_grad_audits = [grad_audit for grad_audit in grad_audits if grad_audit.is_satisfied]
        is_satisfied = len(satisfied_grad_audits) >= at_least
        grad_audit = GradAudit(requirement=requirement, is_satisfied=is_satisfied, children=grad_audits)
        return grad_audit, unused_courses
    

class Requirement(models.Model):
    name = models.CharField(max_length=50,
                            help_text="e.g., PhysicsBS Technical Electives, or GenEd Literature;"
                            "first part is helpful for searching (when creating a major).")
    
    display_name = models.CharField(max_length=50,
                                    help_text="e.g., Technical Electives, or Literature;"
                                    "this is the title that will show up when students"
                                    "do a graduation audit.")

    min_required_credit_hours = models.PositiveIntegerField(default=0)
    constraints = models.ManyToManyField(Constraint, related_name='constraints', blank=True)
    requirements = models.ManyToManyField('self', symmetrical=False, blank=True, related_name = 'sub_requirements')
    courses = models.ManyToManyField('Course', related_name = 'courses', blank=True)

    def __unicode__(self):
        try:
            student = self.student
            return '{} {} {}'.format(student, student.entering_year, self.name)
        except Student.DoesNotExist:
            return self.name

    def required_courses(self):
        return list(self.courses.all())

    def all_courses(self):
        """ Returns the required from this requirement and any sub requirements."""
        reqs = self.requirements.all()
        req_courses = [list(req.all_courses()) for req in reqs]
        return self.required_courses() + (list(itertools.chain(*req_courses)))

    def audit(self, courses, unused_courses = None, student = None):
        """
        Returns a grad_audit, unused_courses
        """
        def _inner(self, courses,unused_courses):
            """Examines a requirements constraints to create a grad_audit. 
            If all constraints are met, gradAudit is_satisfied. """
            
            grad_audit = GradAudit(requirement=self, student=student)

            is_satisfied = True
            for constraint in self.constraints.all():
                child_audit, unused_courses = constraint.audit(courses, self, unused_courses)
                is_satisfied = is_satisfied and child_audit.is_satisfied
                grad_audit.addMessage(constraint.name)
                grad_audit.addMetCourses(child_audit.met_courses)
                if child_audit.requirement == self: grad_audit.addChildren(*child_audit.children)
            
            grad_audit.is_satisfied = is_satisfied
            return grad_audit, unused_courses

        if unused_courses is None: unused_courses = set(courses)
        return _inner(self, courses, unused_courses)


    def child_requirements(self):
        return self.requirements.all()

    def met_courses(self, courseOfferings, consider_all_courses=False):
        """ Returns a dictionary that maps a required_course to the course_offering/ substitute 
        that fulfills it. If all is true examines the courses from this requirement and sub_requirements.
        Otherwise only considers courses for this requirement.
        """
        offering_meets_course = lambda offering, course: offering.course == course

        if consider_all_courses:
            courses = self.all_courses()
        else:
            courses = self.required_courses()

        met_courses = {}
        for course in courses:
            for co in courseOfferings:
                if offering_meets_course(co, course):
                    met_courses[course] = co
        return met_courses
            
    class Meta:
        ordering = ['display_name', ]

    @classmethod
    def make_graduation_requirement(cls, student):
        """Creates a students graduation requirement if they do not have one.
        Modifies an existing one making sure that it always has the correct 
        majors, minors, etc. Should be called whenever you need to setup a 
        students graduation requirements, or even access them."""

        foundational_core = cls.objects.get(name='Foundational Core')
        if student.graduationRequirement is None:
            req = cls(name='Graduation Requirements',
                      display_name='Graduation Requirements')
            req.save()
            req.requirements.add(foundational_core)
            
            req.requirements.add(*[m.requirement for m in student.majors.all()])
            req.requirements.add(*[m.requirement for m in student.minors.all()])

            student.graduationRequirement = req
            student.save()

        else: 
            req = student.graduationRequirement

            valid_requirements = [foundational_core]
            valid_requirements.extend([m.requirement for m in student.majors.all()])
            valid_requirements.extend([m.requirement for m in student.minors.all()])
            
            requirements =  req.requirements.all()

            invalid_requirements = set(requirements) - set(valid_requirements)
            req.requirements.remove(*invalid_requirements)

            missing_requirements = set(valid_requirements) - set(requirements)
            req.requirements.add(*missing_requirements)
        
        req.constraints.add(Constraint.objects.get(name='All sub requirements need to be satisfied'))
        return req
