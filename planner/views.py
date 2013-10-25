from collections import namedtuple
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.shortcuts import render, redirect
from django.template import RequestContext
from forms import *
from models import *

def home(request):
    return render(request, 'home.html')

def student_registration(request):
    if request.user.is_authenticated():
        return redirect('profile')
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        print form.fields
        if form.is_valid():
            user = User.objects.create_user(username = form.cleaned_data['username'],
                                            email = form.cleaned_data['email'],
                                            password = form.cleaned_data['password'])
            user.save()
            print form.cleaned_data['classification']
            if form.cleaned_data['classification']=="1":
                student = Student(user=user,
                                  first_name=form.cleaned_data['first_name'],
                                  last_name=form.cleaned_data['last_name'],
                                  entering_year=form.cleaned_data['entering_year'],
                                  )
                student.save()
                student.majors = form.cleaned_data['majors']
                student.save()
            else:
                professor = Professor(user=user,
                                      first_name=form.cleaned_data['first_name'],
                                      last_name=form.cleaned_data['last_name'])
                professor.save()
            current_user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            login(request,current_user)
            return redirect('profile')
        else:
            return render(request, 'register.html', {'form': form})

        # Should the other things (advising notes, etc.) be included here as well?!?

    else:
        # User is not submitting the form; show them the blank registration form.
        form = RegistrationForm()
        context = {'form': form}
        return render(request, 'register.html', context)

@login_required
def profile(request):
    # TODO: add search functionality.
    user = request.user
    courses = CourseOffering.objects.all()

    if user.is_student():
        isProfessor = False
        professorName = ''
        advisee = None
    else:
        isProfessor = True
        professorName = user.professor.full_name
        advisee = user.professor.advisee

    context = { 'isProfessor': isProfessor,
                'professorName': professorName,
                'advisee': advisee,
		'course': courses }
    return render(request, 'profile.html', context)

@login_required
def update_major(request):
    student = request.user.student

    if request.method == 'POST':
        form = UpdateMajorForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return redirect('profile')
        else:
            return render(request, 'updatemajor.html', {'form': form})
    else:
        form = UpdateMajorForm(instance=student)
        context = {'form': form}
        return render(request, 'updatemajor.html', context)


# problems:
# --> I think the way that I have passed the object's id is not the best way to do it....
# --> maybe look here:
#     http://stackoverflow.com/questions/9013697/django-how-to-pass-object-object-id-to-another-template
@login_required
def update_student_semester(request, semester_id):
    semester = Semester.objects.get(id=semester_id)
    student = request.user.student
    course_subs = CourseSubstitution.objects.filter(student=student)
    if request.method == 'POST':
        form = AddCourseForm(request.POST, instance=student, semester=semester)
        if form.is_valid():
            planned_courses = form.cleaned_data['planned_courses']
            for co in planned_courses:
                student.planned_courses.add(co)
            return redirect('four_year_plan')
        else:
            return render(request, 'updatestudentsemester.html',
                          {'form' : form, 'semester_id' : semester_id, 'course_subs' : course_subs})
    else:
        form = AddCourseForm(instance=student, semester=semester)
        context = {'form' : form,
                   'semester_id' : semester_id,
                   'course_subs' : course_subs}
        return render(request, 'updatesemester.html', context)


def advisee_required(fn):
    """Makes sure that if user is a professor, they have an
    advisee. If they don't redirect to update advisee."""
    def _f(request, *args, **kwargs):
        if request.user.is_professor():
            student = request.user.professor.advisee
            if student is None:
                url = reverse('update_advisee')
                return redirect(url + '?next={}'.format(request.path))
            else:
                return fn(request, *args, **kwargs)
        else:
            return fn(request, *args, **kwargs)
    return _f

@login_required
@advisee_required
def display_advising_notes(request):
    if request.user.is_student():
        student = request.user.student
    else:
        student = request.user.professor.advisee

    context = {'student': student,
               'advisingNotes': AdvisingNote.objects.filter(student=student),
               'isProfessor': request.user.is_professor()}
    return render(request, 'advisingnotes.html', context)

@login_required
def add_new_advising_note(request):
    student = request.user.student
    if request.method == 'POST':
        form = AddAdvisingNoteForm(request.POST)
        if form.is_valid():
            p1 = AdvisingNote(student=student)
            p1.note = form.cleaned_data['note']
            p1.save()
            return redirect('advising_notes')
        else:
            return render(request, 'addAdvisingNote.html', {'form': form})
    else:
        # User is not submitting the form; show them the blank add semester form
        form = AddAdvisingNoteForm()
        context = {'form': form}
        return render(request, 'addAdvisingNote.html', context)

@login_required
def update_advising_note(request, advising_note_id):
    advisingNote = AdvisingNote.objects.get(pk = advising_note_id)
    student_id = request.user.get_student_id()
    incoming_id = advisingNote.student.id
    if student_id != incoming_id:
        return redirect('profile')

    if request.method == 'POST':
        form = AddAdvisingNoteForm(request.POST, instance=advisingNote)
        if form.is_valid():
            form.save()
            return redirect('advising_notes')
        else:
            return render(request, 'addAdvisingNote.html', {'form': form})
    else:
        # user is not submitting the form; show them the blank add semester form
        form = AddAdvisingNoteForm(instance=advisingNote)
        context = {'form': form}
        return render(request, 'addAdvisingNote.html', context)

@login_required
def delete_advising_note(request, id):
    instance = AdvisingNote.objects.get(pk = id)
    request_id = request.user
    request_id = request.user.get_student_id()
    incoming_id = instance.student.id
    if request_id != incoming_id:
        return redirect('profile')

    instance.delete()
    return redirect('advising_notes')




@login_required
@advisee_required
def display_four_year_plan(request):
    if request.user.is_professor():
        student = request.user.professor.advisee
    else:
        student = request.user.student

    total_credit_hours = student.credit_hours_in_plan()
    context = {'student': student,
               'four_year_plan' : student.four_year_plan(),
               'totalhrsfouryears': total_credit_hours,
               'credithrmaxreached': total_credit_hours > 159,
               'isProfessor': request.user.is_professor()}
    return render(request, 'fouryearplan.html', context)

@login_required
@advisee_required
def display_grad_audit(request):
    if request.user.is_student():
        student = request.user.student
    else:
        student = request.user.professor.advisee

    if student.has_major:
        grad_audit,unused_courses = student.grad_audit()
        sp_cc_information = student.sp_cc_information()
        credit_hours_in_plan = student.credit_hours_in_plan()

        context = {'student': student,
                   'hasMajor' : student.has_major(),
                   'isProfessor' : request.user.is_professor(),
                   'unusedcourses': unused_courses,
                   'unusedcredithours': sum([courseOffering.credit_hours
                                             for courseOffering in unused_courses]),
                   'SPlist': sp_cc_information['sps'],
                   'CClist': sp_cc_information['ccs'],
                   'numSPs': sp_cc_information['num_sps'],
                   'numCCs': sp_cc_information['num_ccs'],
                   'SPreq' : sp_cc_information['sps_met'],
                   'CCreq' : sp_cc_information['ccs_met'],
                   'totalhrsfouryears': credit_hours_in_plan,
                   'credithrmaxreached': credit_hours_in_plan > 160 } # TODO: put 160 credit hour limit into a model

        context['requirement_blocks'] =  GradAuditTemplate(grad_audit).requirementBlocks()
        return render(request, 'graduationaudit.html', context)



@login_required
def add_course_substitution(request, semester_id):
    student = request.user.student
    semester = Semester.objects.get(id=semester_id)
    substitute = CourseSubstitution(student=student, semester=semester)

    if request.method == 'POST':
        form = AddCourseSubstitution(request.POST,instance=substitute)
        if form.is_valid():
            form.save()
            next = request.GET.get('next', 'profile')
            return redirect(next)
        else:
            return render(request, 'add_course_substitute.html', {'form': form})
    else:
        form = AddCourseSubstitution(instance=substitute)
        context = {'form': form}
        return render(request, 'add_course_substitute.html', context)


@login_required
def edit_course_substitution(request, course_sub_id):
    course_sub = CourseSubstitution.objects.get(id=course_sub_id)
    request_id = request.user.get_student_id()
    incoming_id = course_sub.student.id

    if request_id != incoming_id:
        return redirect('profile')

    if request.method == 'POST':
        form = AddCourseSubstitution(request.POST, instance=course_sub)
        if form.is_valid():
            form.save()
            next = request.GET.get('next', 'profile')
            return redirect(next)
        else:
            return render(request, 'add_course_substitute.html', {'form': form})
    else:
        form = AddCourseSubstitution(instance=course_sub)
        context = {'form': form}
        return render(request, 'add_course_substitute.html', context)


@login_required
def delete_course_substitution(request, course_sub_id ):
    course_sub = CourseSubstitution.objects.get(id=course_sub_id)
    request_id = request.user.get_student_id()
    incoming_id = course_sub.student.id
    if request_id != incoming_id:
        return redirect('profile')
    course_sub.delete()
    next = request.GET.get('next', 'profile')
    return redirect(next)

@login_required
def add_course_to_plan(request, offering_id):
    student = request.user.student
    student.planned_courses.add(CourseOffering.objects.get(id=offering_id))
    next = request.GET.get('next', 'profile')
    return redirect(next)

@login_required
def remove_course_from_plan(request, offering_id):
    student = request.user.student
    student.planned_courses.remove(CourseOffering.objects.get(id=offering_id))
    next = request.GET.get('next', 'profile')
    return redirect(next)


@login_required
def move_course_to_new_semester(request, old_offering_id, new_offering_id):
    student = request.user.student
    old_offering = CourseOffering.objects.get(id=old_offering_id)
    new_offering = CourseOffering.objects.get(id=new_offering_id)
    student.planned_courses.add(new_offering)
    student.planned_courses.remove(old_offering)
    next = request.GET.get('next', 'profile')
    return redirect(next)



def prepopulate_student_semesters(studentid):
    student = Student.objects.all().get(pk = studentid)
    major = student.major
    enteringyear=student.entering_year
    datalist = PrepopulateSemesters.objects.all().filter(Q(major=major) &
                                                         Q(enteringyear__year=enteringyear))
    temp_data=StudentSemesterCourses.objects.all().filter(student=student)
    ssclist=[]
    for ssc in temp_data:
        if ssc.semester !=0:  # don't include pre-TU ssc object here
            ssclist.append([ssc.id, ssc.actual_year, ssc.semester])

    if len(datalist) == 0:
        return False

    # Assume that there is only one PrepopulateSemester object for a given major and
    # entering year!!!
    popsemdata=datalist[0]

    semarray = []

    semarray.append([enteringyear,     1, popsemdata.freshman_fall_courses.all()])
    semarray.append([enteringyear + 1, 2, popsemdata.freshman_jterm_courses.all()])
    semarray.append([enteringyear + 1, 3, popsemdata.freshman_spring_courses.all()])
    semarray.append([enteringyear + 1, 4, popsemdata.freshman_summer_courses.all()])

    semarray.append([enteringyear + 1, 1, popsemdata.sophomore_fall_courses.all()])
    semarray.append([enteringyear + 2, 2, popsemdata.sophomore_jterm_courses.all()])
    semarray.append([enteringyear + 2, 3, popsemdata.sophomore_spring_courses.all()])
    semarray.append([enteringyear + 2, 4, popsemdata.sophomore_summer_courses.all()])

    semarray.append([enteringyear + 2, 1, popsemdata.junior_fall_courses.all()])
    semarray.append([enteringyear + 3, 2, popsemdata.junior_jterm_courses.all()])
    semarray.append([enteringyear + 3, 3, popsemdata.junior_spring_courses.all()])
    semarray.append([enteringyear + 3, 4, popsemdata.junior_summer_courses.all()])

    semarray.append([enteringyear + 3, 1, popsemdata.senior_fall_courses.all()])
    semarray.append([enteringyear + 4, 2, popsemdata.senior_jterm_courses.all()])
    semarray.append([enteringyear + 4, 3, popsemdata.senior_spring_courses.all()])
    semarray.append([enteringyear + 4, 4, popsemdata.senior_summer_courses.all()])

    for sem in semarray:
        tempsem=sem[1]
        tempyear=sem[0]
        for ssc in ssclist:
            if ssc[1] == tempyear and ssc[2] == tempsem:
                sscid=ssc[0]
                for course in sem[2]:
                    course_id = course.id
                    StudentSemesterCourses.objects.get(pk = sscid).courses.add(course_id)

    return True


@login_required
def update_advisee(request):
    if request.user.is_student():
        return redirect('profile')

    professor = request.user.professor
    if request.method == 'POST':
        form = AddAdviseeForm(request.POST, instance=professor)
        if form.is_valid():
            form.save()
            return redirect(request.GET.get('next', 'profile'))
        else:
            return render(request, 'addadvisee.html', {'form': form})
    else:
        form = AddAdviseeForm(instance=professor)
        context = {'form': form}
        return render(request, 'addadvisee.html', context)

# PUT in something to limit search results!!!!  maybe only display first 20 records or
# something!!!  !!! do we need to do any security stuff here to make sure this is really a
# prof?!?
@login_required
def search(request):
    """Determine the # of students enrolled in courses that match a search request."""

    if request.user.is_student():
        return redirect('profile')

    if 'q' in request.GET and request.GET['q']:
        q = request.GET['q']

        courses = filter(lambda c: q.upper() in c.abbrev.replace(' ',''), Course.objects.all())
        course_infos = []
        print courses
        for course in courses:
            offering_data = []
            for offering in CourseOffering.objects.filter(course=course):
                offering_info = {'id' : offering.id,
                                 'semester' : offering.semester,
                                 'num_students' : len(offering.students.all())}
                offering_data.append(offering_info)
            course = {'name' : course.title, 'abbrev' : course.abbrev, 'offerings' : offering_data}
            course_infos.append(course)

        context={'courses':course_infos,'query':q, 'datablock':course_infos}
        return render(request, 'course_enrollment_results.html',context)
    else:
        return redirect('profile')


@login_required
def view_enrolled_students(request,offering_id):
    """Display students enrolled in a given course offering"""

    if request.user.is_student():
        return redirect('profile')

    courseOffering = CourseOffering.objects.get(id=offering_id)
    course_name = "{} {}".format(courseOffering.course.title, courseOffering.course.abbrev)
    semester = courseOffering.semester
    semester_name = "{} of {}".format(semester.name, semester.year.actual_year(semester.name))
    students = courseOffering.students.all()
    context={'coursename':course_name,'semestername':semester_name,'studentlist':students}
    return render(request, 'student_enrollment_results.html', context)
