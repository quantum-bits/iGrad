from django.db import models
from django.forms import ModelForm

# possible to make all of the semesters in the Student class an array of some sort?  that would be much more convenient!

#
# next: take the contact form and move it over to this folder and get
# it working; then understand how it works, and try to change it to make
# an automatic version of the student form
#
# here's how to extract all courses for a given semester:
# from django.db.models import Q
# jterm_course_list = Course.objects.filter(Q(semester__actual_year="2013") & Q(semester__semester_of_acad_year = 1))
# for courses in jterm_course_list:
#    print courses.id
#
# information on having a user login, including a template and login stuff:
# https://docs.djangoproject.com/en/dev/topics/auth/
#
# this seems to show how to choose from among the manytomanyfield choices:
# http://stackoverflow.com/questions/1226760/filter-manytomany-box-in-django-admin
# ...the idea would be to choose only those courses that are offered in a
# given semester, instead of all the courses
# look at limit_choices_to on this same page...could be useful!
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

    Y2012 = 2012
    Y2013 = 2013
    Y2014 = 2014
    Y2015 = 2015
    Y2016 = 2016
    Y2017 = 2017
    Y2018 = 2018
    Y2019 = 2019

    YEAR_CHOICES = (
        (Y2012, '2012'),
        (Y2013, '2013'),
        (Y2014, '2014'),
        (Y2015, '2015'),
        (Y2016, '2016'),
        (Y2017, '2017'),
        (Y2018, '2018'),
        (Y2019, '2019'),
    )

    name = models.CharField(max_length=50,help_text="e.g., Fa12 or J13")
    semester_of_acad_year = models.IntegerField(choices=SEMESTER_CHOICES, default = FALL_SEMESTER)
    actual_year = models.PositiveIntegerField(choices=YEAR_CHOICES, default = Y2012)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['semester_of_acad_year']
    

class Department(models.Model):
    name = models.CharField(max_length=50, help_text="e.g., Physics and Engineering")
# e.g., name = 'Physics and Engineering'

    def __unicode__(self):
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
    department = models.ForeignKey(Department)
    credit_hours = models.PositiveIntegerField(choices = CREDIT_CHOICES, default=cr3)
    semester = models.ManyToManyField(Semester)
    prereqs = models.ManyToManyField("self", symmetrical = False, related_name='pre_courses', blank=True)
    coreqs = models.ManyToManyField("self", symmetrical = False, related_name='co_courses', blank=True)
    sp = models.BooleanField(default = False, verbose_name="SP")
    cc = models.BooleanField(default = False, verbose_name="CC")

    def __unicode__(self):
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

    CREDZERO = 0
    CREDONE = 1
    CREDTWO = 2
    CREDTHR = 3
    CREDFOUR = 4
    CREDFIVE = 5

    name = models.CharField(max_length=50,
       help_text="e.g., PhysicsBS Technical Electives, or GenEd Literature; first part is for searching (when creating a major) and will not be seen by user.")
    AND_or_OR_Requirement = models.IntegerField(choices=AND_OR_CHOICES, default = ANDREQ, 
       help_text = "Choose AND if all are required, OR if a subset is required.")
    minimum_number_of_credit_hours = models.IntegerField(default = 10)
    list_order = models.PositiveIntegerField(default = 1, help_text="Preferred place in the list of requirements; it is OK if numbers are repeated or skipped.")
# This will be used to order the requirements when viewed by the user.
    text_for_user = models.CharField(max_length=50, blank = True, help_text="Optional helpful text for the user.")
    courselist = models.ManyToManyField(Course, help_text = "Select courses for this requirement.")


    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Major(models.Model):

    name = models.CharField(max_length=50,
       help_text="e.g., Physics BS or Mathematics BA.")
    major_requirements = models.ManyToManyField(RequirementBlock)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Student(models.Model):
    last_name = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    email = models.EmailField(blank=True, verbose_name='e-mail')
    major = models.ForeignKey(Major)
    entering_year = models.PositiveIntegerField(default=2012, help_text = "e.g., 2012")

    freshman_fall_courses = models.ManyToManyField(Course, related_name='frfa', blank=True)
    freshman_jterm_courses = models.ManyToManyField(Course, related_name='frj', blank=True)
    freshman_spring_courses = models.ManyToManyField(Course, related_name='frsp', blank=True)
    freshman_summer_courses = models.ManyToManyField(Course, related_name='frsum', blank=True)

    sophomore_fall_courses = models.ManyToManyField(Course, related_name='sofa', blank=True)
    sophomore_jterm_courses = models.ManyToManyField(Course, related_name='soj', blank=True)
    sophomore_spring_courses = models.ManyToManyField(Course, related_name='sosp', blank=True)
    sophomore_summer_courses = models.ManyToManyField(Course, related_name='sosum', blank=True)

    junior_fall_courses = models.ManyToManyField(Course, related_name='jrfa', blank=True)
    junior_jterm_courses = models.ManyToManyField(Course, related_name='jrj', blank=True)
    junior_spring_courses = models.ManyToManyField(Course, related_name='jrsp', blank=True)
    junior_summer_courses = models.ManyToManyField(Course, related_name='jrsum', blank=True)

    senior_fall_courses = models.ManyToManyField(Course, related_name='srfa', blank=True)
    senior_jterm_courses = models.ManyToManyField(Course, related_name='srj', blank=True)
    senior_spring_courses = models.ManyToManyField(Course, related_name='srsp', blank=True)
    senior_summer_courses = models.ManyToManyField(Course, related_name='srsum', blank=True)

    super_senior_fall_courses = models.ManyToManyField(Course, related_name='spsrfa', blank=True)
    super_senior_jterm_courses = models.ManyToManyField(Course, related_name='spsrj', blank=True)
    super_senior_spring_courses = models.ManyToManyField(Course, related_name='spsrsp', blank=True)
    super_senior_summer_courses = models.ManyToManyField(Course, related_name='spsrsum', blank=True)

    pre_TU_courses = models.ManyToManyField(Course, related_name='pretu', blank=True)

    advising_notes = models.CharField(max_length=50, blank=True)

    def __unicode__(self):
        return u'%s %s' % (self.first_name, self.last_name)

    class Meta:
        ordering = ['last_name']

#class StudentForm(ModelForm):
#    class Meta:
#        model = Student
