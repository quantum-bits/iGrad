from django.contrib import admin
from four_year_plan_v1.majors.models import Semester, Department, Course, RequirementBlock, Major, Student, StudentSemesterCourses, CreateYourOwnCourse, AdvisingNote, EnteringYear, PrepopulateSemesters, Professor

class SemesterAdmin(admin.ModelAdmin):
    list_display = ('name', 'semester_of_acad_year', 'actual_year')

class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'number', 'credit_hours','sp', 'cc')
#    ordering = ('semester',)
    search_fields = ('name', 'number')
    filter_horizontal = ('semester','prereqs','coreqs',)

class RequirementBlockAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    filter_horizontal = ('courselist',)

class MajorAdmin(admin.ModelAdmin):
    filter_horizontal = ('major_requirements',)

class StudentAdmin(admin.ModelAdmin):
    list_display = ('name','entering_year',)
#    filter_horizontal = ('freshman_fall_courses','freshman_spring_courses','sophomore_fall_courses','sophomore_spring_courses','junior_fall_courses',)

#class StudentAdmin(admin.ModelAdmin):
#    list_display = ('last_name','first_name','email', 'major', 'entering_year',)
#    filter_horizontal = ('freshman_fall_courses','freshman_spring_courses','sophomore_fall_courses','sophomore_spring_courses','junior_fall_courses',)

class AdvisingNoteAdmin(admin.ModelAdmin):
    list_display = ('student','note',)

class CreateYourOwnCourseAdmin(admin.ModelAdmin):
    list_display = ('name','number','student','equivalentcourse',)

class EnteringYearAdmin(admin.ModelAdmin):
    list_display = ('year',)

class PrepopulateSemestersAdmin(admin.ModelAdmin):
    search_fields = ('name','major',)
    filter_horizontal = ('enteringyear',
                         'freshman_fall_courses','freshman_jterm_courses',
                         'freshman_spring_courses','freshman_summer_courses',
                         'sophomore_fall_courses','sophomore_jterm_courses',
                         'sophomore_spring_courses','sophomore_summer_courses',
                         'junior_fall_courses','junior_jterm_courses',
                         'junior_spring_courses','junior_summer_courses',
                         'senior_fall_courses','senior_jterm_courses',
                         'senior_spring_courses','senior_summer_courses',)

class ProfessorAdmin(admin.ModelAdmin):
    list_display = ('name','advisee',)

admin.site.register(Semester, SemesterAdmin)
admin.site.register(Department)
admin.site.register(Course, CourseAdmin)
admin.site.register(RequirementBlock, RequirementBlockAdmin)
admin.site.register(Major, MajorAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(StudentSemesterCourses)
admin.site.register(AdvisingNote)
admin.site.register(CreateYourOwnCourse)
admin.site.register(EnteringYear, EnteringYearAdmin)
admin.site.register(PrepopulateSemesters, PrepopulateSemestersAdmin)
admin.site.register(Professor, ProfessorAdmin)

