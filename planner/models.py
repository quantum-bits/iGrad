from django.db import models
from django.forms import ModelForm
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.db.models import Sum

# here's how to extract all courses for a given semester:
# from django.db.models import Q
# jterm_course_list = Course.objects.filter(Q(semester__actual_year="2013") & Q(semester__semester_of_acad_year = 1))
# for courses in jterm_course_list:
#    print courses.id
#
# information on having a user login, including a emplate and login stuff:
# https://docs.djangoproject.com/en/dev/topics/auth/
#
# the following might help, too:
# http://stackoverflow.com/questions/7133455/django-limit-choices-to-doesnt-work-on-manytomanyfield
#
# also, here: https://docs.djangoproject.com/en/dev/ref/models/fields/
#

class Semester(models.Model):
    FALL_SEMESTER = 1
    JTERM_SEMESTER = 2
    SPRING_SEMESTER = 3
    SUMMER_SEMESTER = 4
    SEMESTER_CHOICES = (
        (FALL_SEMESTER, 'Fall'),
        (JTERM_SEMESTER, 'J-term'),
        (SPRING_SEMESTER, 'Spring'),
        (SUMMER_SEMESTER, 'Summer'),
    )

    Y2009 = 2009
    Y2010 = 2010
    Y2011 = 2011
    Y2012 = 2012
    Y2013 = 2013
    Y2014 = 2014
    Y2015 = 2015
    Y2016 = 2016
    Y2017 = 2017
    Y2018 = 2018
    Y2019 = 2019
    Y2020 = 2020
    Y2021 = 2021
    Y2022 = 2022

    YEAR_CHOICES = (
        (Y2009, '2009'),
        (Y2010, '2010'),
        (Y2011, '2011'),
        (Y2012, '2012'),
        (Y2013, '2013'),
        (Y2014, '2014'),
        (Y2015, '2015'),
        (Y2016, '2016'),
        (Y2017, '2017'),
        (Y2018, '2018'),
        (Y2019, '2019'),
        (Y2020, '2020'),
        (Y2021, '2021'),
        (Y2022, '2022'),
    )

    name = models.CharField(max_length=50,help_text="e.g., Fa12 or J13")
    semester_of_acad_year = models.IntegerField(choices=SEMESTER_CHOICES, default = FALL_SEMESTER)
    actual_year = models.PositiveIntegerField(choices=YEAR_CHOICES, default = Y2012)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['semester_of_acad_year']


class Department(models.Model):
    name = models.CharField(max_length=50, help_text="e.g., Physics and Engineering")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class Course(models.Model):

    cr0 = 0
    cr1 = 1
    cr2 = 2
    cr3 = 3
    cr4 = 4
    cr5 = 5
    cr6 = 6

    CREDIT_CHOICES = (
        (cr0, '0'),
        (cr1, '1'),
        (cr2, '2'),
        (cr3, '3'),
        (cr4, '4'),
        (cr5, '5'),
        (cr6, '6'),
    )

    name = models.CharField(max_length=50,help_text="e.g., University Physics I & Lab")
    number = models.CharField(max_length=10, help_text="e.g., PHY211")
    department = models.ForeignKey(Department, on_delete=models.PROTECT)
    credit_hours = models.PositiveIntegerField(choices = CREDIT_CHOICES, default=cr3)
    semester = models.ManyToManyField(Semester)
    prereqs = models.ManyToManyField("self", symmetrical = False,
                                     related_name='pre_courses', blank=True)
    coreqs = models.ManyToManyField("self", symmetrical = False,
                                    related_name='co_courses', blank=True)
    sp = models.BooleanField(default = False, verbose_name="SP")
    cc = models.BooleanField(default = False, verbose_name="CC")

    def __str__(self):
        return self.number

    class Meta:
        ordering = ['number']

class RequirementBlock(models.Model):
    ANDREQ = 1
    ORREQ = 2
    AND_OR_CHOICES = (
        (ANDREQ, 'AND'),
        (ORREQ, 'OR')
    )

    name = models.CharField(max_length=50, help_text="e.g., PhysicsBS Technical Electives, or GenEd Literature; first part is helpful for searching (when creating a major).")
    display_name = models.CharField(max_length=50, help_text="e.g., Technical Electives, or Literature; this is the title that will show up when students do a graduation audit.")

    AND_or_OR_Requirement = models.IntegerField(choices=AND_OR_CHOICES, default = ANDREQ,
                                                help_text = "Choose AND if all are required, OR if a subset is required.")
    minimum_number_of_credit_hours = models.IntegerField(default = 10)
    list_order = models.PositiveIntegerField(default = 1, help_text="Preferred place in the list of requirements; it is OK if numbers are repeated or skipped.")
    # This will be used to order the requirements when viewed by the user.
    text_for_user = models.CharField(max_length=200, blank = True, help_text="Optional helpful text for the user; will appear in the graduation audit.")
    courselist = models.ManyToManyField(Course, help_text = "Select courses for this requirement.")


    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Major(models.Model):

    name = models.CharField(max_length=50,
                            help_text="e.g., Physics BS or Mathematics BA.")
    major_requirements = models.ManyToManyField(RequirementBlock)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class UserProxy(User):
    class Meta:
        proxy = True

    def __str__(self):
        return self.get_full_name()

    def info(self):
        info = [ "id '{0}'".format(self.get_username()) ]
        if self.is_student():
            info.append('student')
        if self.is_professor():
            info.append('professor')
        return ", ".join(info)

    def is_student(self):
        try:
            if self.student:
                return True
        except Student.DoesNotExist:
            return False

    def get_student_id(self):
        assert(self.is_student())
        return self.student.id

    def is_professor(self):
        try:
            if self.professor:
                return True
        except Professor.DoesNotExist:
            return False

    def get_professor_id(self):
        assert(self.is_professor())
        return self.professor.id

from django.contrib.auth.backends import ModelBackend
class ProxiedModelBackend(ModelBackend):
    def get_user(self, user_id):
        try:
            return UserProxy.objects.get(pk=user_id)
        except UserProxy.DoesNotExist:
            return None

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    name = models.CharField(max_length=100)
    major = models.ForeignKey(Major, blank=True, null=True, on_delete=models.PROTECT)
    entering_year = models.PositiveIntegerField(default=2012, help_text = "e.g., 2015")
    # might need to add null=True above as well....
    #    birthday = models.DateField(blank=True, null=True)
    # Update 5/9/2013 - Items to add
    # current_status = models.CharField(max_length=100) Freshman - Senior For display purposes

    def __str__(self):
        return self.name

    def num_credit_hours(self, student_semester_course):
        credit_hours = student_semester_course.courses.aggregate(Sum('credit_hours'))
        credit_hours = credit_hours['credit_hours__sum']
        credit_hours = 0 if credit_hours is None else credit_hours

        cyo_courses = CreateYourOwnCourse.objects.filter(student=self, semester=student_semester_course.semester, actual_year=student_semester_course.actual_year)
        cyo_courses = CreateYourOwnCourse.objects.filter(student=self, semester=student_semester_course.semester)
        cyo_courses = cyo_courses.filter(actual_year=student_semester_course.actual_year)
        cyo_courses_hours = cyo_courses.aggregate(Sum('credit_hours'))['credit_hours__sum']
        cyo_courses_hours = 0 if cyo_courses_hours is None else cyo_courses_hours
        return credit_hours + cyo_courses_hours

    class Meta:
        ordering = ['name']


class Professor(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    name = models.CharField(max_length=100)
    advisee = models.ForeignKey(Student, blank=True, null=True, on_delete=models.PROTECT)

    def __str__(self):
        return self.name

class StudentSemesterCourses(models.Model):
    PRETU_SEMESTER = 0
    FALL_SEMESTER = 1
    JTERM_SEMESTER = 2
    SPRING_SEMESTER = 3
    SUMMER_SEMESTER = 4
    SEMESTER_CHOICES = (
        (PRETU_SEMESTER, 'Pre-TU'),
        (FALL_SEMESTER, 'Fall'),
        (JTERM_SEMESTER, 'J-term'),
        (SPRING_SEMESTER, 'Spring'),
        (SUMMER_SEMESTER, 'Summer'),
    )

    PRETU_YEAR = 0
    FRESHMAN_YEAR = 1
    SOPHMORE_YEAR = 2
    JUNIOR_YEAR = 3
    SENIOR_YEAR = 4
    SUPERSENIOR_YEAR = 5
    YEAR_CHOICES = (
        (PRETU_YEAR, 'Pre-TU'),
        (FRESHMAN_YEAR, 'Freshman'),
        (SOPHMORE_YEAR, 'Sophmore'),
        (JUNIOR_YEAR, 'Junior'),
        (SENIOR_YEAR, 'Senior'),
        (SUPERSENIOR_YEAR, 'Super-Senior'),
    )

    semester = models.PositiveIntegerField(choices=SEMESTER_CHOICES, default = FALL_SEMESTER)
    year = models.PositiveIntegerField(choices=YEAR_CHOICES, default = FRESHMAN_YEAR)
    student = models.ForeignKey(Student, related_name='ssc_student', on_delete=models.PROTECT)
    courses = models.ManyToManyField(Course, related_name='semestercourses', blank=True)
    #    actual_year=models.PositiveIntegerField(default='2012')

    class Meta:
        verbose_name_plural = 'Student semester courses'

    def __str__(self):
        return "{0} {1} {2}".format(self.student,
                                    self.get_year_display(),
                                    self.get_semester_display())


    @property
    def actual_year(self):
        if self.semester == 1:
            return self.student.entering_year + self.year - 1
        else:
            return self.student.entering_year + self.year

class CreateYourOwnCourse(models.Model):
    # Objects in this class correspond to courses that are transferred in
    # (and may not correspond exactly to TU courses, e.g., the course may have a
    # different # of credit hours), or courses that are not in the database
    # for some reason.  The student has the option to choose an "equivalent"
    # course at Taylor, for the purpose of the graduation audit.  For example,
    # maybe the student has taken Calc III somewhere else during the summer,
    # but it was a 3-hr course there.  They could choose Calc III at TU
    # as the equivalent course, and it would show up in the graduation audit,
    # but it would show up as being deficient by one hour.
    #
    # the following are the possible choices for "semester":
    #   pre-TU: 0 (irrelevant, in this case, so we assign it "zero")
    #   Fall:   1
    #   J-term: 2
    #   Spring: 3
    #   Summer: 4
    #
    cr0 = 0
    cr1 = 1
    cr2 = 2
    cr3 = 3
    cr4 = 4
    cr5 = 5
    cr6 = 6

    CREDIT_CHOICES = (
        (cr0, '0'),
        (cr1, '1'),
        (cr2, '2'),
        (cr3, '3'),
        (cr4, '4'),
        (cr5, '5'),
        (cr6, '6'),
    )

    Y2009 = 2009
    Y2010 = 2010
    Y2011 = 2011
    Y2012 = 2012
    Y2013 = 2013
    Y2014 = 2014
    Y2015 = 2015
    Y2016 = 2016
    Y2017 = 2017
    Y2018 = 2018
    Y2019 = 2019
    Y2020 = 2020
    Y2021 = 2021
    Y2022 = 2022

    YEAR_CHOICES = (
        (Y2009, '2009'),
        (Y2010, '2010'),
        (Y2011, '2011'),
        (Y2012, '2012'),
        (Y2013, '2013'),
        (Y2014, '2014'),
        (Y2015, '2015'),
        (Y2016, '2016'),
        (Y2017, '2017'),
        (Y2018, '2018'),
        (Y2019, '2019'),
        (Y2020, '2020'),
        (Y2021, '2021'),
        (Y2022, '2022'),
    )

    name = models.CharField(max_length=50,help_text="e.g., Underwater Basket Weaving")
    number = models.CharField(max_length=10, help_text="e.g., UBW101")
    credit_hours = models.PositiveIntegerField(choices = CREDIT_CHOICES, default=cr3)
    semester = models.PositiveIntegerField()
    actual_year = models.PositiveIntegerField(choices = YEAR_CHOICES, default=Y2012)
    student = models.ForeignKey(Student, related_name='cyoc_student', on_delete=models.PROTECT)
    equivalentcourse = models.ForeignKey(Course, blank=True, null=True, on_delete=models.PROTECT)
    sp = models.BooleanField(default = False, verbose_name="SP")
    cc = models.BooleanField(default = False, verbose_name="CC")

    def __str__(self):
        return "{0} - {1}".format(self.number, self.name)

class AdvisingNote(models.Model):
    student = models.ForeignKey(Student, related_name='advisingnotes_student', on_delete=models.PROTECT)
    note = models.TextField(max_length=1000, blank=True)
    datestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{0} on {1}".format(self.student, self.datestamp)

class EnteringYear(models.Model):

    Y2009 = 2009
    Y2010 = 2010
    Y2011 = 2011
    Y2012 = 2012
    Y2013 = 2013
    Y2014 = 2014
    Y2015 = 2015
    Y2016 = 2016
    Y2017 = 2017
    Y2018 = 2018
    Y2019 = 2019
    Y2020 = 2020
    Y2021 = 2021
    Y2022 = 2022

    YEAR_CHOICES = (
        (Y2009, '2009'),
        (Y2010, '2010'),
        (Y2011, '2011'),
        (Y2012, '2012'),
        (Y2013, '2013'),
        (Y2014, '2014'),
        (Y2015, '2015'),
        (Y2016, '2016'),
        (Y2017, '2017'),
        (Y2018, '2018'),
        (Y2019, '2019'),
        (Y2020, '2020'),
        (Y2021, '2021'),
        (Y2022, '2022'),
    )

    year = models.PositiveIntegerField(choices=YEAR_CHOICES, default = Y2012)

    def __str__(self):
        return str(self.year)

class PrepopulateSemesters(models.Model):
    name = models.CharField(max_length=100,help_text="e.g., Physics BS, entering odd years")
    enteringyear = models.ManyToManyField(EnteringYear)
    major = models.ForeignKey(Major, on_delete=models.PROTECT)

    freshman_fall_courses = models.ManyToManyField(Course, related_name='frfall', blank=True)
    freshman_jterm_courses = models.ManyToManyField(Course, related_name='frjterm', blank=True)
    freshman_spring_courses = models.ManyToManyField(Course, related_name='frspring', blank=True)
    freshman_summer_courses = models.ManyToManyField(Course, related_name='frsummer', blank=True)

    sophomore_fall_courses = models.ManyToManyField(Course, related_name='sofall', blank=True)
    sophomore_jterm_courses = models.ManyToManyField(Course, related_name='sojterm', blank=True)
    sophomore_spring_courses = models.ManyToManyField(Course, related_name='sospring', blank=True)
    sophomore_summer_courses = models.ManyToManyField(Course, related_name='sosummer', blank=True)

    junior_fall_courses = models.ManyToManyField(Course, related_name='jrfall', blank=True)
    junior_jterm_courses = models.ManyToManyField(Course, related_name='jrjterm', blank=True)
    junior_spring_courses = models.ManyToManyField(Course, related_name='jrspring', blank=True)
    junior_summer_courses = models.ManyToManyField(Course, related_name='jrsummer', blank=True)

    senior_fall_courses = models.ManyToManyField(Course, related_name='srfall', blank=True)
    senior_jterm_courses = models.ManyToManyField(Course, related_name='srjterm', blank=True)
    senior_spring_courses = models.ManyToManyField(Course, related_name='srspring', blank=True)
    senior_summer_courses = models.ManyToManyField(Course, related_name='srsummer', blank=True)

    class Meta:
        verbose_name_plural = 'Prepopulate semesters'

    def __str__(self):
        return self.name
