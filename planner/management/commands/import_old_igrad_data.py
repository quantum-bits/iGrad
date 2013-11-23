from django.core.management.base import BaseCommand, CommandError
from planner.models import AcademicYear, Course, CourseOffering, Student, User, SemesterName, Semester, Professor, Major

import json
import re

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        self.majors  = {}
        with open('majors.txt', 'r') as major_f:
            for line in major_f:
                old_name, new_name = line.split(',')
                try:
                    self.majors[old_name] = Major.objects.get(name=new_name.rstrip())
                except Major.DoesNotExist:
                    self.majors[old_name] = None
        try:
            json_filename = args[0]
            with open(json_filename, 'r') as json_f:
                igrad_data = json.loads(json_f.read())
                self.load_data(igrad_data)
        except IndexError:
            raise CommandError('Filename not supplied.')
        except IOError:
            raise CommandError('Filename: {} Does not exist.'.format(json_filename))


                
    def load_data(self, igrad_data):

        self.load_users(igrad_data)
        self.load_majors(igrad_data)
        self.load_students(igrad_data)
        #self.load_courses(igrad_data)
        #self.load_semesters(igrad_data)
        #self.load_course_offerings(igrad_data)
        self.load_professors(obj for obj in igrad_data if obj['model'] == 'planner.professor')

    def load_users(self, igrad_data):
        """Loads users from igrad_data. Creates a list of users so
        that later load calls can use them."""
        self.users = {}
        for obj in igrad_data:
            if obj['model'] == 'auth.user':

                fields = obj['fields']
                user_id = obj['pk'] 
                username = fields['username']
                is_superuser = fields['is_superuser']
                password = fields['password']
                email = fields['email']
                
                user,created = User.objects.get_or_create(username=username)
                
                if created:
                    user.is_superuser = is_superuser
                    user.password = password
                    user.email = email
                    user.save()

                self.users[user_id] = user
                
    def load_majors(self, igrad_data):
        self.major_names = {}
        for obj in igrad_data:
            if obj['model'] == 'planner.major':
                major_id = obj['pk']
                self.major_names[major_id] = obj['fields']['name']

    def load_students(self, igrad_data):
        self.students = {}
        for obj in igrad_data:
            if obj['model'] == 'planner.student':
                fields = obj['fields']
                user = self.users[fields['user']]
                entering_year = AcademicYear.objects.get(begin_on__year = fields['entering_year'])
                student_id = user.username
                try:
                    first_name, last_name = fields['name'].split(' ', 1)
                except ValueError: 
                    last_name = fields['name']
                    first_name = ''
                
                try:
                    student =  Student.objects.get(user=user)
                except Student.DoesNotExist:
                    student = Student(user=user, entering_year=entering_year, student_id=student_id)

                student.last_name = last_name
                student.first_name = first_name
                student.save()

                major_id = fields['major']
                major = self.majors[self.major_names[major_id]]
                if major is not None:
                    student.majors.add(major)
                self.students[obj['pk']] = student

    def load_professors(self, professors):
        self.professors = {}
        for obj in professors:
            fields = obj['fields']
            user = self.users[fields['user']]
            advisee = self.students[fields['advisee']]
            try:
                first_name, last_name = fields['name'].split(' ', 1)
            except ValueError:
                last_name = fields['name']

            try:
                professor = Professor.objects.get(user=user)
            except Professor.DoesNotExist:
                professor = Professor(user=user, advisee=advisee)

            professor.last_name = last_name
            professor.first_name = first_name
            professor.save()
            
            
    def load_courses(self, igrad_data):
        self.courses = {}
        course_number = re.compile(r'(?P<subject>[A-Z]{3})(?P<number>\d{3})')
        for obj in igrad_data:
            if obj['model'] == 'planner.course':
                course_id = obj['pk']
                fields = obj['fields']
                number = fields['number']

                match = course_number.match(number)
                if match:
                    subj, number = match.group('subject'), match.group('number')
                    try:
                        course = Course.objects.get(subject__abbrev=subj, number=int(number))
                        self.courses[course_id] = (course, fields['credit_hours'])
                    except Course.DoesNotExist:
                        print 'Course: {}{} Not found'.format(subj, number)

    def load_semesters(self, igrad_data):
        self.semesters = {}
        abbrev_name = {'Fa' : 'Fall', 
                       'J'  : 'J-Term',
                       'Sp' : 'Spring',
                       'Sum' : 'Summer'}

        semester_name = re.compile(r'(?P<abbrev>[A-Za-z]+)(?P<year>\d+)')
        for obj in igrad_data:
            if obj['model'] == 'planner.semester':
                semester_id = obj['pk']
                fields = obj['fields']
                name  = fields['name']
                match = semester_name.match(name)
                if match:
                    abbrev = match.group('abbrev')
                    year = match.group('year')
                    semesterName = SemesterName.objects.get(name=abbrev_name[abbrev])
                    try:
                        year = AcademicYear.objects.get(begin_on__year=2000 + int(year))
                        semester = Semester.objects.get(name=semesterName, year=year)
                    except AcademicYear.MultipleObjectsReturned:
                        print 'AcademicYear: {}{} returns multiple objects.'.format(abbrev, year)
                    except Semester.DoesNotExist:
                        print 'Semester: {}{} Does not exist.'.format(abbrev, year)
                    self.semesters[semester_id] = semester
                else:
                    print 'Unmatch Semester'
                

    def _get_semester(self, student, semester, year):
        semester_to_name = [None, 'Fall', 'J-Term', 'Spring','Summer']
        years_offset = [None, 0, 1, 2, 3, 4]
    
        name = semester_to_name[semester]
        offset = years_offset[year]
        if name is None or offset is None: 
            return None
        return Semester.objects.get(name__name=semester_to_name[semester],
                                    year = student.entering_year + years_offset[year])


    def load_course_offerings(self, igrad_data):
        for obj in igrad_data:
            if obj['model'] == 'planner.studentsemestercourses':
                fields = obj['fields']
                try:
                    student = self.students[fields['student']]
                    semester = self._get_semester(student, fields['semester'], fields['year'])
                    if semester is not None:
                        for course_id in fields['courses']:
                            course, credit_hours = self.courses[course_id]
                            offering,_ = CourseOffering.objects.get_or_create(course=course, credit_hours=int(credit_hours), semester=semester)
                            student.planned_courses.add(offering)
                except KeyError:
                    print 'Student: {} Does not exist.'.format(fields['student'])
                

    def load_transfer_courses(self, igrad_data):
        pass
    



