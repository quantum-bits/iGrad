from django.db import models

from common_models import *
from campus_models import *

import logging
logger = logging.getLogger(__name__)

    

# class StudentSemesterCourses
#
# This class used to represent courses taken by a student in a given semester. In the
# updated data model, this relationship is captured in the CourseTaken model, which
# relates a Student to CourseOffering. The CourseOffering has an associated Semester
# object, which tells us when the student took that course.


# class CreateYourOwnCourse
#
# This class has been replaced by the more sensibly-named TransferCourse.

class CourseSubstitution(models.Model):
    """Course transferred from another institution."""
    university = models.ForeignKey(University, related_name='course_substitutions',
                                   blank=True, null=True)
    title = models.CharField(max_length=80)
    credit_hours = models.PositiveIntegerField(default=3)
    semester = models.ForeignKey(Semester, blank=True, null=True)
    equivalent_course = models.ForeignKey(Course, related_name='course_substitutions')
    student = models.ForeignKey(Student, related_name='course_substitutions')

    def __unicode__(self):
        return self.title


class AdvisingNote(StampedModel):
    student = models.ForeignKey(Student, related_name='advising_notes')
    note = models.TextField()

    def __unicode__(self):
        return "{0} on {1}".format(self.student, self.updated_at)


class ClassStanding(models.Model):
    """Class standing (e.g., freshman, sophomore, ...)"""
    seq = models.PositiveIntegerField(default=10)
    name = models.CharField(max_length=20)

    class Meta:
        ordering = ['seq']

    def __unicode__(self):
        return self.name


# class PrepopulateSemesters is now class DegreeProgram
class DegreeProgram(StampedModel):
    """Courses in a degree program"""
    name = models.CharField(max_length=100, help_text="e.g., Physics BS, entering odd years")
    entering_year = models.CharField(max_length=1, choices=Course.SCHEDULE_YEAR_CHOICES)
    major = models.ForeignKey(Major, related_name='degree_programs')

    def __unicode__(self):
        return self.name


class DegreeProgramCourse(StampedModel):
    """Single course in a degree program"""
    degree_program = models.ForeignKey(DegreeProgram)
    course = models.ForeignKey(Course)
    class_standing = models.ForeignKey(ClassStanding)
    semester_name = models.ForeignKey(SemesterName)





