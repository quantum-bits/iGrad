from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
#from django.contrib.auth import authenticate, login
from studentform.forms import RegistrationForm, LoginForm, AddStudentSemesterForm, AddPreTUCoursesForm
from four_year_plan_v1.majors.models import Course, Student, StudentSemesterCourses, PreTUCourses
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q

def Home(request):
    return render_to_response('home.html', context_instance=RequestContext(request))

def StudentRegistration(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/profile/')
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(username = form.cleaned_data['username'], 
                                            email = form.cleaned_data['email'], 
                                            password = form.cleaned_data['password'])
            user.save()
            student = user.get_profile() # <--- I don't quite get what's happening here....
            student.name = form.cleaned_data['name']
            student.entering_year = form.cleaned_data['entering_year']
            student.advising_notes = form.cleaned_data['advising_notes']
            student.major = form.cleaned_data['major']
#            student = Student(user=user, name=form.cleaned_data['name'],
#                              entering_year=form.cleaned_data['entering_year'],
#                              pre_TU_courses=form.cleaned_data['pre_TU_courses'],
#                              advising_notes = form.cleaned_data['advising_notes'],
#                              birthday = form.cleaned_data['birthday'],
#                              major = form.cleaned_data['major'])
            student.save()
            
            yearlist=[1,2,3,4,5]
            semesterlist=[1,2,3,4]
            for yeartemp in yearlist:
                for semestertemp in semesterlist:
                    p1 = StudentSemesterCourses(student=student, year = yeartemp, semester = semestertemp)
                    p1.save()

            p2 = PreTUCourses(student=student)
            p2.save()

            return HttpResponseRedirect('/profile/')
        else:
            return render_to_response('register.html', {'form': form}, context_instance=RequestContext(request))

# should the other things (advising notes, etc.) be included here as well?!?

    else:
        '''user is not submitting the form; show them the blank registration form'''
        form = RegistrationForm()
        context = {'form': form}
        return render_to_response('register.html', context, context_instance = RequestContext(request))

@login_required
def Profile(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/login/')
    student = request.user.get_profile
# Note: to access the email address in the view, you could set it to
# email = student.user.email
    context = {'student': student}
    return render_to_response('profile.html', context, context_instance=RequestContext(request))
		

def LoginRequest(request):
    if request.user.is_authenticated(): # so that the user can't login twice....
        return HttpResponseRedirect('/profile/')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        context = {'form': form}
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password'] # local variables that can be used
# see if username/password combo authenticates; returns None otherwise
            student = authenticate(username=username, password=password) 
            if student is not None: # authentication passed
                login(request, student) # log the person in using django's login function
                return HttpResponseRedirect('/profile/')
            else: # let person try to login again
                return render_to_response('login.html', context, context_instance = RequestContext(request))
        else: #form wasn't valid....
            return render_to_response('login.html', context, context_instance = RequestContext(request))
    else:
        ''' user is not submitting the form; show the login form '''
        form = LoginForm()
        context = {'form': form}
        return render_to_response('login.html', context, context_instance = RequestContext(request))

def LogoutRequest(request):
    logout(request)
    return HttpResponseRedirect('/home/')


# Problems:
# 1. THE FOLLOWING lets anyone change anyone else's semester!!!  just type .../updatesemester/12/ or something
#   ...OK...fixed at least somewhat...maybe someone with knowledge of cookies, etc., could still work around this.
#    --> I think the way that I have passed the object's id is not the best way to do it....
#    --> maybe look here: http://stackoverflow.com/questions/9013697/django-how-to-pass-object-object-id-to-another-template
@login_required
def UpdateStudentSemester(request, id):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/login/')
    instance = StudentSemesterCourses.objects.get(pk = id)
    studentnamerecord = instance.student.name
    studentnamerequestingaccess = request.user.get_profile().name
    year=instance.actual_year
    semester=instance.semester

# The following statement kicks the person out if he/she is trying to hack into
# someone else's "update student semester" function...if the name of the requester
# and the person who "belongs" to the id are different, the requester gets sent
# back to his/her profile as punishment :)
    if studentnamerecord != studentnamerequestingaccess:
        return HttpResponseRedirect('/profile/')

    if request.method == 'POST':
        my_kwargs = dict(
            instance=instance,
            actualyear=year,
            semester=semester
        )
        form = AddStudentSemesterForm(request.POST, **my_kwargs)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/fouryearplan/')
        else:
            return render_to_response('updatesemester.html', {'form': form}, context_instance=RequestContext(request))
    else:
        '''user is not submitting the form; show them the blank add semester form'''
        my_kwargs = dict(
            instance=instance,
            actualyear=year,
            semester=semester
        )
        form = AddStudentSemesterForm(**my_kwargs)
        context = {'form': form, 'namerecord':studentnamerecord,
                   'namerequestingaccess':studentnamerequestingaccess}
        return render_to_response('updatesemester.html', context, context_instance = RequestContext(request))

@login_required
def PreTUCredit(request, id):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/login/')
    instance = PreTUCourses.objects.get(pk = id)
    studentnamerecord = instance.student.name
    studentnamerequestingaccess = request.user.get_profile().name

# The following statement kicks the person out if he/she is trying to hack into
# someone else's "update student semester" function...if the name of the requester
# and the person who "belongs" to the id are different, the requester gets sent
# back to his/her profile as punishment :)
    if studentnamerecord != studentnamerequestingaccess:
        return HttpResponseRedirect('/profile/')

    if request.method == 'POST':
        form = AddPreTUCoursesForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/fouryearplan/')
        else:
            return render_to_response('updatePreTUCourses.html', {'form': form}, context_instance=RequestContext(request))
    else:
        '''user is not submitting the form; show them the blank add semester form'''
        form = AddPreTUCoursesForm(instance=instance)
        context = {'form': form}
        return render_to_response('updatePreTUCourses.html', context, context_instance = RequestContext(request))

@login_required
def DisplayFourYearPlan(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/login/')
    studentlocal = request.user.get_profile
    tempdataPreTU=PreTUCourses.objects.all().filter(student=studentlocal)

    totalcredithoursfouryears=0

    preTUblock=[]
    for sem1 in tempdataPreTU:
        tempcoursename=[]
        totalpreTUcredithrs = 0
        for cc in sem1.courses.all():
            totalpreTUcredithrs = totalpreTUcredithrs + cc.credit_hours
            tempcoursename.append([cc.name,cc.number,cc.credit_hours,cc.sp,cc.cc])
        preTUblock.append([sem1.student.name, tempcoursename, sem1.id, totalpreTUcredithrs])
        totalcredithoursfouryears=totalcredithoursfouryears+totalpreTUcredithrs

    tempdata=StudentSemesterCourses.objects.all().filter(student=studentlocal)
    datablock=[]
# "alphabetize" the semesters...
    for sem1 in tempdata:
        tempcoursename=[]
        if sem1.semester == 1:
            sem = 'dFall'
        elif sem1.semester == 2:
            sem = 'aJ-term'
        elif sem1.semester == 3:
            sem = 'bSpring'
        else:
            sem = 'cSummer'
        totalcredithrs = 0
#        assert False, locals()
        for cc in sem1.courses.all():
            totalcredithrs = totalcredithrs + cc.credit_hours
            tempcoursename.append([cc.name,cc.number,cc.credit_hours,cc.sp,cc.cc])
#        assert False, locals()
        datablock.append([sem1.actual_year, sem, sem1.student.name, tempcoursename, sem1.id, totalcredithrs])
        totalcredithoursfouryears=totalcredithoursfouryears+totalcredithrs
#        assert False, locals()
# initial sort
    datablock2 = sorted(datablock, key=lambda rrow: (rrow[0], rrow[1]))
# now rename the semesters (this is pretty ugly!!)
    datablock3 = []
    for row in datablock2:
        if row[1]=='aJ-term':
            temprow=[row[0], 'J-term', row[2], row[3], row[4], row[5]]
        elif row[1]=='bSpring':
            temprow=[row[0], 'Spring', row[2], row[3], row[4], row[5]]
        elif row[1]=='cSummer':
            temprow=[row[0], 'Summer', row[2], row[3], row[4], row[5]]
        else:
            temprow=[row[0], 'Fall', row[2], row[3], row[4], row[5]]
        datablock3.append(temprow)    

    context = {'student': studentlocal, 'preTUblock':preTUblock,'datablock':datablock3,
               'totalhrsfouryears':totalcredithoursfouryears}
    return render_to_response('fouryearplan.html', context, context_instance=RequestContext(request))
		

@login_required
def DisplayGradAudit(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/login/')
    studentlocal = request.user.get_profile
    tempdata = StudentSemesterCourses.objects.all().filter(student=studentlocal)
    tempdata2 = Student.objects.all().filter(user=request.user)
# I think tempdata2 doesn't "evaluate" until you do something with it (like render it in 
# the template, or evaluate it in a for loop...hence I do a for loop below, even though
# there is only one object....
    for studenttemp in tempdata2:
        studentmajor = studenttemp.major

    majordatablock = []
    for mr in studentmajor.major_requirements.all():
        courselisttemp=[]
        if mr.AND_or_OR_Requirement == 1:
            AND_OR_comment = "All of the following are required."
        else:
            AND_OR_comment = "Choose from the following."
        for course in mr.courselist.all():
            templist=tempdata.filter(Q(courses__number=course.number))
            coursetaken=[]
            for ctaken in templist:
                if ctaken.semester == 1:
                    tempsem="Fall"
                if ctaken.semester == 2:
                    tempsem="J-term"
                if ctaken.semester == 3:
                    tempsem="Spring"
                if ctaken.semester == 4:
                    tempsem="Summer"
                coursetaken.append([tempsem, ctaken.actual_year])
            courselisttemp.append([course.name, course.number, 
                                   course.credit_hours, course.sp, course.cc, coursetaken])
        majordatablock.append([mr.list_order, mr.name, AND_OR_comment, 
                                   mr.minimum_number_of_credit_hours, 
                                   mr.text_for_user, courselisttemp])
        
        majordatablock2 = sorted(majordatablock, key=lambda rrow: (rrow[0]))

        

    tempdataPreTU=PreTUCourses.objects.all().filter(student=studentlocal)

    preTUblock=[]
    for sem1 in tempdataPreTU:
        tempcoursename=[]
        for cc in sem1.courses.all():
            tempcoursename.append([cc.name,cc.number,cc.credit_hours,cc.sp,cc.cc])
        preTUblock.append([sem1.student.name, tempcoursename, sem1.id])


    datablock=[]
# "alphabetize" the semesters...
    for sem1 in tempdata:
        tempcoursename=[]
        if sem1.semester == 1:
            sem = 'dFall'
        elif sem1.semester == 2:
            sem = 'aJ-term'
        elif sem1.semester == 3:
            sem = 'bSpring'
        else:
            sem = 'cSummer'
        for cc in sem1.courses.all():
            tempcoursename.append([cc.name,cc.number,cc.credit_hours,cc.sp,cc.cc])
        datablock.append([sem1.actual_year, sem, sem1.student.name, tempcoursename, sem1.id])
# initial sort
    datablock2 = sorted(datablock, key=lambda rrow: (rrow[0], rrow[1]))
# now rename the semesters (this is pretty ugly!!)
    datablock3 = []
    for row in datablock2:
        if row[1]=='aJ-term':
            temprow=[row[0], 'J-term', row[2], row[3], row[4]]
        elif row[1]=='bSpring':
            temprow=[row[0], 'Spring', row[2], row[3], row[4]]
        elif row[1]=='cSummer':
            temprow=[row[0], 'Summer', row[2], row[3], row[4]]
        else:
            temprow=[row[0], 'Fall', row[2], row[3], row[4]]
        datablock3.append(temprow)    

    context = {'student': studentlocal, 'studentmajor': studentmajor, 'majordatablock': majordatablock2}
    return render_to_response('graduationaudit.html', context, context_instance=RequestContext(request))
		
