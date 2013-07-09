from django.contrib import admin
from planner.models import *


class SemesterAdmin(admin.ModelAdmin):
    list_display = ('name', 'year')

class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'department', 'number', 'credit_hours',)
    search_fields = ('title', 'number')
    filter_horizontal = ('schedule_semester','prereqs','coreqs',)

class RequirementAdmin(admin.ModelAdmin):
    filter_horizontal = ('constraints', 'requirements', 'courses',)

class RequirementBlockAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    filter_horizontal = ('courselist',)

class MajorAdmin(admin.ModelAdmin):
    search_fields = ('name', 'department',)

class StudentAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'entering_year',)

class AdvisingNoteAdmin(admin.ModelAdmin):
    list_display = ('student','note',)

class CourseSubstitutionAdmin(admin.ModelAdmin):
    list_display = ('student','equivalent_course',)


class DegreeProgramAdmin(admin.ModelAdmin):
    search_fields = ('name','major',)

class DegreeProgramCourseAdmin(admin.ModelAdmin):
    search_fields = ('degree_program',)


admin.site.register(AcademicYear)
admin.site.register(AdvisingNote)
admin.site.register(Constraint)
admin.site.register(CreditHour)
admin.site.register(Course, CourseAdmin)
admin.site.register(CourseAttribute)
admin.site.register(CourseOffering)
admin.site.register(CourseSubstitution, CourseSubstitutionAdmin)
admin.site.register(DegreeProgram, DegreeProgramAdmin)
admin.site.register(DegreeProgramCourse, DegreeProgramCourseAdmin)
admin.site.register(Department)
admin.site.register(FacultyMember)
admin.site.register(Major, MajorAdmin)
admin.site.register(Minor)
admin.site.register(Requirement, RequirementAdmin)
admin.site.register(School)
admin.site.register(Semester, SemesterAdmin)
admin.site.register(SemesterName)
admin.site.register(SemesterDateDefault)
admin.site.register(Student, StudentAdmin)
admin.site.register(Subject)
admin.site.register(University)
