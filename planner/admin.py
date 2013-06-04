from django.contrib import admin
from planner.models import *

class SemesterAdmin(admin.ModelAdmin):
    list_display = ('name', 'year')

class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'department', 'number', 'credit_hours')
    search_fields = ('title', 'number')
    filter_horizontal = ('schedule_semester','prereqs','coreqs',)

class RequirementBlockAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    filter_horizontal = ('courselist',)

class MajorAdmin(admin.ModelAdmin):
    search_fields = ('name', 'department',)

class StudentAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'entering_year',)

class AdvisingNoteAdmin(admin.ModelAdmin):
    list_display = ('student','note',)

class TransferCourseAdmin(admin.ModelAdmin):
    list_display = ('name','number','student','equivalentcourse',)


class DegreeProgramAdmin(admin.ModelAdmin):
    search_fields = ('name','major',)

class DegreeProgramCourseAdmin(admin.ModelAdmin):
    search_fields = ('degree_program',)


admin.site.register(CourseOffering)
admin.site.register(SemesterName)
admin.site.register(FacultyMember)
admin.site.register(Semester, SemesterAdmin)
admin.site.register(Department)
admin.site.register(Course, CourseAdmin)
admin.site.register(RequirementBlock, RequirementBlockAdmin)
admin.site.register(Major, MajorAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(AdvisingNote)
admin.site.register(AcademicYear)
admin.site.register(TransferCourse)
admin.site.register(DegreeProgram, DegreeProgramAdmin)
admin.site.register(DegreeProgramCourse, DegreeProgramCourseAdmin)
admin.site.register(Minor)
admin.site.register(University)
admin.site.register(School)
