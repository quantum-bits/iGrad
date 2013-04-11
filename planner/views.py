from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
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
        if form.is_valid():
            user = User.objects.create_user(username = form.cleaned_data['username'],
                                            email = form.cleaned_data['email'],
                                            password = form.cleaned_data['password'])
            user.save()

            student = user.get_profile()
            student.name = form.cleaned_data['name']
            student.entering_year = form.cleaned_data['entering_year']
            student.major = form.cleaned_data['major']
            student.save()

            yearlist = [0, 1, 2, 3, 4, 5]
            semesterlist = [1, 2, 3, 4]
            for yeartemp in yearlist:
                if yeartemp == 0:
                    semestertemp = 0
                    p1 = StudentSemesterCourses(student=student,
                                                year=yeartemp,
                                                semester=semestertemp)
                    p1.save()
                else:
                    for semestertemp in semesterlist:
                        p1 = StudentSemesterCourses(student=student,
                                                    year=yeartemp,
                                                    semester=semestertemp)
                        p1.save()

            if student.major is not None:
                coursesadded = prepopulate_student_semesters(student.id)
            else:
                coursesadded = False

            return redirect('profile')
        else:
            return render(request, 'register.html', {'form': form})

        # should the other things (advising notes, etc.) be included here as well?!?

    else:
        # User is not submitting the form; show them the blank registration form.
        form = RegistrationForm()
        context = {'form': form}
        return render(request, 'register.html', context)

@login_required
def profile(request):
    user = request.user

    if user.is_student():
        isProfessor = False
        professorname = ''
        adviseename = ''
    else:
        isProfessor = True
        professorname = user.professor.name
        adviseeobj = user.professor.advisee
        if adviseeobj is None:
            adviseename = 'None currently selected'
        else:
            adviseename = user.professor.advisee.name

    # Note: to access the email address in the view, you could set it to
    # email = student.user.email
    context = { 'isProfessor': isProfessor,
                'professorname': professorname,
                'advisee': adviseename }
    return render(request, 'profile.html', context)

@login_required
def update_major(request, id):
    requestid = request.user.get_profile().id
    incomingid = int(id)

    if requestid != incomingid:
        return redirect('profile')

    instance = Student.objects.get(pk=id)

    if request.method == 'POST':
        form = update_majorForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('profile')
        else:
            return render(request, 'updatemajor.html', {'form': form})
    else:
        # User is not submitting the form; show them the blank add major form.
        form = update_majorForm(instance=instance)
        context = {'form': form}
        return render(request, 'updatemajor.html', context)

def login_request(request):
    if request.user.is_authenticated(): # so that the user can't login twice....
        return redirect('profile')
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
                # check if the "professor" is actually a professor....
                professor = request.user.get_profile
                temp = Professor.objects.all().filter(user=professor)
                if len(temp) == 0: # this is a student, not a professor
                    return redirect('profile')
                else: # this is a professor; clear "advisee" field if it is currently not None....
                    advisee = temp[0].advisee # advisee is a Student object
                    if advisee is not None:
                        professorid = temp[0].id
                        Professor.objects.filter(id=professorid).update(advisee=None)
                    return redirect('profile')
            else: # let person try to login again
                return render(request, 'login.html', context)
        else: #form wasn't valid....
            return render(request, 'login.html', context)
    else:
        #  user is not submitting the form; show the login form 
        form = LoginForm()
        context = {'form': form}
        return render(request, 'login.html', context)

def logout_request(request):
    # Check if the "professor" is actually a professor, if so, clear "advisee" object
    # before logging out.
    professor = request.user.get_profile
    temp = Professor.objects.all().filter(user=professor)
    if len(temp) != 0: # this is a professor
        advisee = temp[0].advisee # advisee is a Student object
        if advisee is not None:
            professorid = temp[0].id
            Professor.objects.filter(id=professorid).update(advisee=None)
    logout(request)
    return HttpResponseRedirect('/home/')


# Problems: 
# --> I think the way that I have passed the object's id is not the best way to do it....
# --> maybe look here:
#     http://stackoverflow.com/questions/9013697/django-how-to-pass-object-object-id-to-another-template
@login_required
def update_student_semester(request, id):
    instance = StudentSemesterCourses.objects.get(pk = id)

    # The following statement kicks the person out if he/she is trying to hack into
    # someone else's "update student semester" function...if the name of the requester and
    # the person who "belongs" to the id are different, the requester gets sent back to
    # his/her profile as punishment :)
    requestid = request.user.get_student_id()
    incomingid = instance.student.id
    if requestid != incomingid:
        return redirect('profile')

    year=instance.actual_year
    semester=instance.semester
    student_local=request.user
    studentcreatedcourses = CreateYourOwnCourse.objects.all().filter(Q(student=student_local)
                           & Q(semester = semester) & Q(actual_year = year))
    
    courselist= Course.objects.filter(Q(sospring=1) & Q(semester__actual_year=year) & Q(semester__semester_of_acad_year = semester))
    current_course_list = Course.objects.filter(Q(semester__actual_year=year) & Q(semester__semester_of_acad_year = semester))

    sccdatablock=[]
    for scc in studentcreatedcourses:
        if scc.equivalentcourse:
            eqnum = ", equiv to "+scc.equivalentcourse.number
        else:
            eqnum  =  ""
        if scc.sp:
            SPtemp = ", SP"
        else:
            SPtemp = ""
        if scc.cc:
            CCtemp = ", CC"
        else:
            CCtemp = ""
        sccdatablock.append({'cname':scc.name,
                             'cnumber':scc.number,
                             'ccredithrs':scc.credit_hours,
                             'csemester':scc.semester,
                             'cyear':scc.actual_year,
                             'equivalentcourse':eqnum,
                             'sp':SPtemp,
                             'cc':CCtemp,
                             'courseid':scc.id})

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
            return render(request, 'updatesemester.html',
                          {'form': form, 'sccdatablock':sccdatablock})
    else:
        # User is not submitting the form; show them the blank add semester form.
        my_kwargs = dict(
            instance=instance,
            actualyear=year,
            semester=semester
        )
        form = AddStudentSemesterForm(**my_kwargs)
        context = {'form': form,
                   'sccdatablock':sccdatablock,
                   'instanceid':id,
		   'courselist': courselist,
		   'current_course_list': current_course_list,
		   'semester': semester}
        return render(request, 'updatesemester.html', context)


@login_required
def display_advising_notes(request):
    if request.user.is_student():
        isProfessor = False
        student_local = request.user.student
    else:
        isProfessor = True
        student_local = request.user.professor.advisee
        if student_local is None:
            # No advisee currently selected; go pick one first
            return HttpResponseRedirect('/changeadvisee/3/')

    tempdata = AdvisingNote.objects.all().filter(student=student_local)

    datablock = []
    ii = 0
    for advnotes in tempdata:
        ii = ii + 1
        datablock.append([advnotes.datestamp, advnotes.note, advnotes.id, ii])

    context = {'student': student_local,
               'datablock': datablock,
               'isProfessor': isProfessor}
    return render(request, 'advisingnotes.html', context)


@login_required
def add_new_advising_note(request):
    # The following list should just have one element(!)...hence "listofstudents[0]" is
    # used in the following....
    listofstudents = Student.objects.all().filter(user=request.user)

    if request.method == 'POST':
        form = AddAdvisingNoteForm(request.POST)
        if form.is_valid():
            p1 = AdvisingNote(student=listofstudents[0])
            p1.note = form.cleaned_data['note']
            p1.save()
            return HttpResponseRedirect('/advisingnotes/')
        else:
            return render(request, 'addadvisingnote.html', {'form': form})
    else:
        # user is not submitting the form; show them the blank add semester form
        form = AddAdvisingNoteForm()
        context = {'form': form}
        return render(request, 'addadvisingnote.html', context)


@login_required
def update_advising_note(request, id):
    instance = AdvisingNote.objects.get(pk = id)
    requestid = request.user.get_profile().id
    incomingid = instance.student.id
    if requestid != incomingid:
        return redirect('profile')

    if request.method == 'POST':
        form = AddAdvisingNoteForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/advisingnotes/')
        else:
            return render(request, 'addadvisingnote.html', {'form': form})
    else:
        # user is not submitting the form; show them the blank add semester form
        form = AddAdvisingNoteForm(instance=instance)
        context = {'form': form}
        return render(request, 'addadvisingnote.html', context)

@login_required
def delete_advising_note(request, id):
    instance = AdvisingNote.objects.get(pk = id)
    requestid = request.user.get_profile().id
    incomingid = instance.student.id
    if requestid != incomingid:
        return redirect('profile')

    instance.delete()
    return HttpResponseRedirect('/advisingnotes/')

@login_required
def display_four_year_plan(request):
    print request.user.is_student()
    if request.user.is_student():
        isProfessor = False
        student_local = request.user
    else:
        isProfessor = True
        student_local = request.user.professor.advisee
        if student_local is None:
            # No advisee currently selected; go pick one first.
            return HttpResponseRedirect('/changeadvisee/1/')

    totalcredithoursfouryears = 0
    tempdata = StudentSemesterCourses.objects.all().filter(student=student_local)
    tempdata2 = CreateYourOwnCourse.objects.all().filter(student=student_local)

    enteringyear = tempdata[0].student.entering_year

    studentid = tempdata[0].student.id
    prenotmetlist, conotmetlist = pre_co_req_check(studentid)

    # ssclist is used for later on when we try to find other semesters that a given course
    # is offered.
    ssclist=[]
    for ssc in tempdata:
        if ssc.semester !=0:
            # Don't include pre-TU ssc object here
            numcrhrsthissem = 0
            for course in ssc.courses.all():
                numcrhrsthissem = numcrhrsthissem + course.credit_hours
            # Now add in credit hours from any create your own type courses
            tempdata4 = tempdata2.filter(Q(semester=ssc.semester)&Q(actual_year=ssc.actual_year))
            for course in tempdata4:
                numcrhrsthissem = numcrhrsthissem + course.credit_hours
            ssclist.append([ssc.id, ssc.actual_year, ssc.semester, numcrhrsthissem])

    termdictionaryalphabetize={0:"aPre-TU", 1:"eFall", 2:"bJ-term", 3:"cSpring", 4:"dSummer"}
    termdictionary={0:"Pre-TU", 1:"Fall", 2:"J-term", 3:"Spring", 4:"Summer"}

    # First, form an array containing the info for the "create your own" type courses
    cyocarray=[]
    for cyoc in tempdata2:
        if cyoc.equivalentcourse:
            equivcoursenamestring = ' (equivalent to: '+cyoc.equivalentcourse.number+')'
        else:
            equivcoursenamestring =''
        cyocarray.append([cyoc.actual_year, termdictionaryalphabetize[cyoc.semester],
                          cyoc.name+equivcoursenamestring,
                          cyoc.number, cyoc.credit_hours, cyoc.sp, cyoc.cc, cyoc.id])

    datablock=[]
    # "Alphabetize" the semesters.
    for sem1 in tempdata:
        semestercontainscyoc = False
        tempcoursename=[]
        semtemp = sem1.semester
        actyeartemp = sem1.actual_year
        semid = sem1.id
        totalcredithrs = 0
        tempcyocarray =[]
        ii = 0
        # Assemble any prereq or coreq comments into a list....
        precocommentlist=[]
        for row in conotmetlist:
            if row[0] == semid:
                precocommentlist.append(row[4] + " is a corequisite for " +
                                        row[2] + "; the requirement is currently not being met.")
        for row in prenotmetlist:
            if row[0] == semid:
                precocommentlist.append(row[4] + " is a prerequisite for " +
                                        row[2] + "; the requirement is currently not being met.")
        for row in cyocarray:
            if row[0] == actyeartemp and row[1] == termdictionaryalphabetize[semtemp]:
                tempcyocarray.append(ii)
            ii=ii+1
        for indexii in reversed(tempcyocarray):
            temparray = cyocarray.pop(indexii)
            totalcredithrs = totalcredithrs+temparray[4]
            iscyoc = True
            semestercontainscyoc = True
            tempcoursename.append({'cname': temparray[2],
                                   'cnumber': temparray[3],
                                   'ccredithours': temparray[4],
                                   'sp': temparray[5],
                                   'cc': temparray[6],
                                   'iscyoc': iscyoc,
                                   'courseid': temparray[7],
                                   'othersemesters': []})
        for cc in sem1.courses.all():
            iscyoc = False
            totalcredithrs = totalcredithrs + cc.credit_hours
            allsemestersthiscourse = cc.semester.all()
            # Form an array of other semesters when this course is offered.
            semarraynonordered = []
            for semthiscourse in allsemestersthiscourse:
                yearotheroffering=semthiscourse.actual_year
                semotheroffering=semthiscourse.semester_of_acad_year
                keepthisone = True
                if yearotheroffering == actyeartemp and semotheroffering == semtemp:
                    keepthisone = False
                else:
                    elementid = -1
                    for row in ssclist:
                        if yearotheroffering == row[1] and semotheroffering == row[2]:
                            elementid = row[0]
                            numhrsthissem = row[3]
                    if elementid == -1:
                        # Id wasn't found, meaning this course offering is not during a
                        # time the student is at TU.
                        keepthisone = False
                if keepthisone == True:
                    semarraynonordered.append([yearotheroffering, semotheroffering,
                                               elementid, numhrsthissem])

            semarrayreordered=reorder_list(semarraynonordered)
            semarray=[]
            for row in semarrayreordered:
                semarray.append({'semester': named_year(enteringyear, row[0], row[1]),
                                 'courseid': row[2],
                                 'numhrsthissem': row[3]})

            tempcoursename.append({'cname': cc.name,
                                   'cnumber': cc.number,
                                   'ccredithours': cc.credit_hours,
                                   'sp': cc.sp,
                                   'cc': cc.cc,
                                   'iscyoc': iscyoc,
                                   'courseid': cc.id,
                                   'othersemesters':semarray})
        datablock.append({'year': actyeartemp,
                          'semestername': termdictionaryalphabetize[semtemp],
                          'studentname': sem1.student.name,
                          'listofcourses': tempcoursename,
                          'semesterid': sem1.id,
                          'totalcredithours': totalcredithrs,
                          'semestercontainscyoc': semestercontainscyoc,
                          'precocommentlist': precocommentlist})
        totalcredithoursfouryears = totalcredithoursfouryears+totalcredithrs

    # initial sort
    datablock2 = sorted(datablock, key=lambda rrow: (rrow['year'], rrow['semestername']))
    datablock3 = []
    for row in datablock2:
        row['semestername'] = row['semestername'][1:]
        datablock3.append(row)

    if totalcredithoursfouryears > 159:
        credithrmaxreached = True
    else:
        credithrmaxreached = False

    # Now organize the 21 (pre-TU, plus 4 for each of freshman,..., super-senior) lists
    # into 6 (pre-TU, freshman, etc.)

    # First check to make sure that there are, in fact, 21 rows....
    if len(datablock3)!=21:
        assert False, locals()

    yearlist=[[0], [1, 2, 3, 4],
              [5, 6, 7, 8], [9, 10, 11, 12],
              [13, 14, 15, 16], [17, 18, 19, 20]]
    datablock4=[]
    for year in yearlist:
        temp=[]
        for semester in year:
            temp.append(datablock3[semester])
        datablock4.append(temp)

    context = {'student': student_local,
               'datablock': datablock4,
               'totalhrsfouryears': totalcredithoursfouryears,
               'credithrmaxreached': credithrmaxreached,
               'isProfessor': isProfessor}
    return render(request, 'fouryearplan.html', context)

@login_required
def display_grad_audit(request):
    if request.user.is_student():
        isProfessor = False
        student_local = request.user
    else:
        isProfessor = True
        student_local = request.user.professor.advisee
        if student_local is None:
            # No advisee currently selected; go pick one first
            return HttpResponseRedirect('/changeadvisee/2/')

    tempdata = StudentSemesterCourses.objects.all().filter(student=student_local)
    tempdata2 = Student.objects.all().filter(user=student_local)
    tempdata3 = CreateYourOwnCourse.objects.all().filter(student=student_local)

    studentid = tempdata[0].student.id
    prenotmetlist, conotmetlist = pre_co_req_check(studentid)

    if tempdata2[0].major is None:
        hasMajor = False
        context = {'student': student_local,'isProfessor': isProfessor,'hasMajor':hasMajor}
        return render(request, 'graduationaudit.html', context)
    else:
        hasMajor = True
        studentmajor = tempdata2[0].major

#    assert False, locals()

    enteringyear=tempdata[0].student.entering_year
    # ssclist is used for later on when we try to find other semesters that a given course
    # is offered.
    ssclist=[]
    for ssc in tempdata:
        if ssc.semester !=0:  # don't include pre-TU ssc object here
            numcrhrsthissem = 0
            for course in ssc.courses.all():
                numcrhrsthissem = numcrhrsthissem + course.credit_hours
            # now add in credit hours from any create your own type courses
            tempdata4 = tempdata3.filter(Q(semester=ssc.semester)&Q(actual_year=ssc.actual_year))
            for course in tempdata4:
                numcrhrsthissem = numcrhrsthissem + course.credit_hours
            ssclist.append([ssc.id, ssc.actual_year, ssc.semester, numcrhrsthissem])

    termdictionary={0:"Pre-TU", 1:"Fall", 2:"J-term", 3:"Spring", 4:"Summer"}

    studentcourselist=[]
    coursenumberlist=[]
    # In the next line of code I use "len()" in order to force django to evaluate the
    # QuerySet...otherwise I get an error saying that the "ManyRelatedManager object is
    # not iterable"
    numrecords=len(tempdata)
    for ssc in tempdata:
        numhrsthissemester = 0
        for course in ssc.courses.all():
            iscyoc = False
            studentcourselist.append([course.name,
                                      ssc.semester,
                                      ssc.actual_year,
                                      course.credit_hours,
                                      course.sp,
                                      course.cc,
                                      iscyoc,
                                      course.number,
                                      ssc.id])
            coursenumberlist.append(course.number)

    # Now add in the user-created ("create your own") type courses.
    for cyoc in tempdata3:
        iscyoc = True
        if cyoc.equivalentcourse:
            equivcoursenamestring = ' (equivalent to: '+cyoc.equivalentcourse.number+')'
            eqcoursenum = cyoc.equivalentcourse.number
        else:
            equivcoursenamestring =''
            eqcoursenum = ''
        studentcourselist.append([cyoc.name+equivcoursenamestring,
                                  cyoc.semester,
                                  cyoc.actual_year,
                                  cyoc.credit_hours,
                                  cyoc.sp,
                                  cyoc.cc,
                                  iscyoc,
                                  cyoc.number,
                                  cyoc.id])
        coursenumberlist.append(eqcoursenum)

    SPlist=[]
    CClist=[]
    numSPs=0
    numCCs=0
    ii=0
    totalcredithoursfouryears=0
    for course in studentcourselist:
        totalcredithoursfouryears=totalcredithoursfouryears+course[3]
        if course[4]:
            #
            # CLEAN UP the following!!! ("Pre-TU" stuff -- this comes up several
            # times...define a function or something!!!!)
            #
            if course[1]==0:
                comment = "Pre-TU"
            else:
                comment = termdictionary[course[1]]+', '+str(course[2])
            SPlist.append({'cname':course[0], 'comment':comment, 'cnumber':course[7]})
            numSPs=numSPs+1
        if course[5]:
            if course[1]==0:
                comment = "Pre-TU"
            else:
                comment = termdictionary[course[1]]+', '+str(course[2])
            CClist.append({'cname':course[0], 'comment':comment, 'cnumber':course[7]})
            numCCs=numCCs+1
        ii=ii+1

    majordatablock = []
    for mr in studentmajor.major_requirements.all():
        precocommentlist=[]
        requirementblockcontainscyoc = False
        courselisttemp=[]
        if mr.AND_or_OR_Requirement == 1:
            AND_OR_comment = "All of the following are required."
        else:
            AND_OR_comment = "Choose from the following."
        total_credit_hours_so_far=0
        courseidlist=[]
        for course in mr.courselist.all():
            iscyoc=False
            cnumber=course.number
            courseid = course.id
            courseidlist.append(courseid)
            numcrhrstaken = ''
            sscid = -1
            try:
                ii=coursenumberlist.index(cnumber)
            except ValueError:
                ii=-1
            if ii !=-1:
                # Assemble any prereq or coreq comments into a list.
                for row in conotmetlist:
                    if row[1] == courseid:
                        precocommentlist.append(row[4] + " is a corequisite for " +
                                                row[2] + "; the requirement is currently not being met.")
                for row in prenotmetlist:
                    if row[1] == courseid:
                        precocommentlist.append(row[4] + " is a prerequisite for " +
                                                row[2] + "; the requirement is currently not being met.")
                courseinfo=studentcourselist.pop(ii)
                cnumbertemp=coursenumberlist.pop(ii)
                numcrhrstaken = courseinfo[3]
                total_credit_hours_so_far+=numcrhrstaken
                semtemp = courseinfo[1]
                actyeartemp = courseinfo[2]
                sscid = courseinfo[8]
                iscyoc = courseinfo[6]
                if courseinfo[1]==0:
                    commentfirstpart = "Pre-TU"
                else:
                    commentfirstpart = named_year(enteringyear, courseinfo[2], courseinfo[1])
                if iscyoc:
                    # This is a "create your own course...need to exercise some caution!
                    requirementblockcontainscyoc = True
                    comment = commentfirstpart+'; ('+str(courseinfo[7])+')*'
                else:
                    # Regular TU course...no problem....
                    comment = commentfirstpart
            else:

                # NOTE: comment is a string if there is a course scheduled; if not, it is
                # False, in which case it is used as a flag for things within graduation
                # html page
                comment=False
                semtemp = -1
                actyeartemp = -1

            # If course is user-defined ("cyoc"), then don't show options for moving the
            # course, so skip the next part
            if iscyoc:
                semarray = []
            else:
                allsemestersthiscourse = course.semester.all()

                # Form an array of other semesters when this course is offered.
                semarraynonordered = []

                for semthiscourse in allsemestersthiscourse:
                    yearotheroffering=semthiscourse.actual_year
                    semotheroffering=semthiscourse.semester_of_acad_year
                    keepthisone = True
                    if yearotheroffering == actyeartemp and semotheroffering == semtemp:
                        keepthisone = False
                    else:
                        elementid = -1
                        for row in ssclist:
                            if yearotheroffering == row[1] and semotheroffering == row[2]:
                                elementid = row[0]
                                numhrsthissem = row[3]
                        if elementid == -1:
                            # Id wasn't found, meaning this course offering is not during
                            # a time the student is at TU
                            keepthisone = False
                    if keepthisone == True:
                        semarraynonordered.append([yearotheroffering,
                                                   semotheroffering,
                                                   elementid,
                                                   numhrsthissem])
                semarrayreordered=reorder_list(semarraynonordered)
                semarray=[]
                for row in semarrayreordered:
                    semarray.append({'semester': named_year(enteringyear, row[0], row[1]),
                                     'courseid': row[2],
                                     'numhrsthissem': row[3]})

            courselisttemp.append({'cname': course.name,
                                   'cnumber': course.number,
                                   'ccredithrs': course.credit_hours,
                                   'sp': course.sp,
                                   'cc': course.cc,
                                   'comment': comment,
                                   'numcrhrstaken': numcrhrstaken,
                                   'courseid': course.id,
                                   'othersemesters': semarray,
                                   'sscid': sscid,
                                   'iscyoc': iscyoc})

        if total_credit_hours_so_far>=mr.minimum_number_of_credit_hours:
            credits_ok=True
        else:
            credits_ok=False

        majordatablock.append({'listorder': mr.list_order,
                               'blockname': mr.display_name,
                               'andorcomment': AND_OR_comment,
                               'mincredithours': mr.minimum_number_of_credit_hours,
                               'textforuser': mr.text_for_user,
                               'courselist': courselisttemp,
                               'credithrs': total_credit_hours_so_far,
                               'creditsok': credits_ok,
                               'blockcontainscyoc': requirementblockcontainscyoc,
                               'precocommentlist': precocommentlist})

        majordatablock2 = sorted(majordatablock, key=lambda rrow: (rrow['listorder']))

        unusedcourses=[]
        unusedcredithours=0
        for course in studentcourselist:
            unusedcredithours=unusedcredithours+course[3]
            if course[1]==0:
                comment = "Pre-TU"
            else:
                comment = named_year(enteringyear, course[2], course[1])
            unusedcourses.append({'cname':course[0],'cnumber':course[7],
                                  'ccredithrs':course[3],'sp':course[4],'cc':course[5],
                                  'comment':comment})

        if numSPs<2:
            SPreq=False
        else:
            SPreq=True
        if numCCs==0:
            CCreq=False
        else:
            CCreq=True

    if totalcredithoursfouryears > 159:
        credithrmaxreached = True
    else:
        credithrmaxreached = False

    context = {'student': student_local,
               'majordatablock': majordatablock2,
               'unusedcourses': unusedcourses,
               'unusedcredithours': unusedcredithours,
               'SPlist': SPlist,
               'CClist': CClist,
               'numSPs': numSPs,
               'numCCs': numCCs,
               'SPreq': SPreq,
               'CCreq': CCreq,
               'totalhrsfouryears': totalcredithoursfouryears,
               'credithrmaxreached': credithrmaxreached,
               'isProfessor': isProfessor,
               'hasMajor': hasMajor}
    return render(request, 'graduationaudit.html', context)


@login_required
def add_new_advising_note(request):
    # The following list should just have one element(!)...hence "listofstudents[0]" is
    # used in the following....
    listofstudents = Student.objects.all().filter(user=request.user)

    if request.method == 'POST':
        form = AddAdvisingNoteForm(request.POST)
        if form.is_valid():
            p1 = AdvisingNote(student=listofstudents[0])
            p1.note = form.cleaned_data['note']
            p1.save()
            return HttpResponseRedirect('/advisingnotes/')
        else:
            return render(request, 'addadvisingnote.html', {'form': form})
    else:
        # User is not submitting the form; show them the blank add semester form
        form = AddAdvisingNoteForm()
        context = {'form': form}
        return render(request, 'addadvisingnote.html', context)

@login_required
def add_create_your_own_course(request,id):
    # The following list should just have one element(!)...hence "listofstudents[0]" is
    # used in the following....
    listofstudents = Student.objects.all().filter(user=request.user)
    ssc = StudentSemesterCourses.objects.get(pk = id)
    requestid = request.user.get_profile().id
    incomingid = ssc.student.id
    if requestid != incomingid:
        return redirect('profile')
    year=ssc.actual_year
    semester=ssc.semester

    if request.method == 'POST':
        form = add_create_your_own_courseForm(request.POST)
        if form.is_valid():
            p1 = CreateYourOwnCourse(student = listofstudents[0])
            p1.name = form.cleaned_data['name']
            p1.number = form.cleaned_data['number']
            p1.credit_hours = form.cleaned_data['credit_hours']
            p1.sp = form.cleaned_data['sp']
            p1.cc = form.cleaned_data['cc']
            p1.semester = semester
            p1.actual_year = year
            p1.equivalentcourse = form.cleaned_data['equivalentcourse']
            p1.save()
            return HttpResponseRedirect('/updatesemester/'+str(id)+'/')
        else:
            return render(request, 'addcreateyourowncourse.html', {'form': form})
    else:
        # User is not submitting the form; show them the blank add create your own course
        # form.
        form = add_create_your_own_courseForm()
        context = {'form': form}
        return render(request, 'addcreateyourowncourse.html', context)


@login_required
def update_create_your_own_course(request,id,id2):
    instance = CreateYourOwnCourse.objects.get(pk = id2)
    ssc = StudentSemesterCourses.objects.get(pk = id)
    requestid = request.user.get_profile().id
    incomingid = ssc.student.id
    incomingid2 = instance.student.id
    if requestid != incomingid:
        return redirect('profile')
    if requestid != incomingid2:
        return redirect('profile')

    if request.method == 'POST':
        form = add_create_your_own_courseForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/updatesemester/'+str(id)+'/')
        else:
            return render(request, 'addcreateyourowncourse.html', {'form': form})
    else:
        # User is not submitting the form; show them the blank add create your own course form
        form = add_create_your_own_courseForm(instance=instance)
        context = {'form': form}
        return render(request, 'addcreateyourowncourse.html', context)


# In the following, "wherefrom" is:
#    0: fouryearplan
#    1: gradaudit
#    2: updatesemester
# "id" is:
#    0: coming from fouryearplan (doesn't matter; not used)
#    0: coming from gradaudit (doesn't matter; not used)
#    ssc id: coming from updatesemester
@login_required
def delete_create_your_own_course(request, wherefrom, id, id2):
    instance = CreateYourOwnCourse.objects.get(pk = id2)

    requestid = request.user.get_profile().id
    incomingid2 = instance.student.id
    if requestid != incomingid2:
        return redirect('profile')

    instance.delete()
    if int(wherefrom) == 2:
        return HttpResponseRedirect('/updatesemester/'+str(id)+'/')
    elif int(wherefrom) == 0:
        return HttpResponseRedirect('/fouryearplan/')
    else:
        return HttpResponseRedirect('/graduationaudit/')

# In the following, wherefrom is:
#    0: fouryearplan
#    1: gradaudit
# id is id of the ssc object
# id2 is id of the course itself
@login_required
def delete_course_inside_SSCObject(request, wherefromflag, id, id2):
    instance = StudentSemesterCourses.objects.get(pk = id)

    requestid = request.user.get_profile().id
    incomingid = instance.student.id
    if requestid != incomingid:
        return redirect('profile')

    StudentSemesterCourses.objects.get(pk = id).courses.remove(id2)
    if int(wherefromflag) == 0:
        return HttpResponseRedirect('/fouryearplan/')
    else:
        return HttpResponseRedirect('/graduationaudit/')

# In the following, wherefrom is:
#    0: fouryearplan
#    1: gradaudit
#
# src_ssc_id is id of the current ssc object (from which the course needs to be deleted); set to
# "-1" if course is not currently being taken (which can happen if request comes from the
# grad audit page)
#
# dest_ssc_id is the id of the new ssc object (to which the course needs to be added)
#
# course_id is the id of the course itself
#
# This routine failed once and I don't know why!!! Said columns for course_id and ssc_id
# were not unique, or something, and gave an integrity error.
@login_required
def move_course_to_new_SSCObject(request, wherefromflag, src_ssc_id, dest_ssc_id, course_id):
    src_ssc_id_int = int(src_ssc_id)

    # Using dest_ssc_id here instead of src_ssc_id, since sometimes we are only creating a
    # new course, and not deleting an old one.
    dest_ssc = StudentSemesterCourses.objects.get(pk=dest_ssc_id)
    request_id = request.user.get_student_id()
    incoming_id = dest_ssc.student.id
    if request_id != incoming_id:
        return redirect('profile')

    if src_ssc_id_int != -1:
        # If src_ssc_id == -1, the course is not being taken, so there is nothing to remove
        instance_old = StudentSemesterCourses.objects.get(pk=src_ssc_id_int)
        incoming_id_old = instance_old.student.id
        if request_id != incoming_id_old:
            return redirect('profile')
        StudentSemesterCourses.objects.get(pk=src_ssc_id).courses.remove(course_id)
    StudentSemesterCourses.objects.get(pk=dest_ssc_id).courses.add(course_id)
    if int(wherefromflag) == 0:
        return redirect('four_year_plan')
    else:
        return redirect('grad_audit')


def pre_co_req_check(studentid):
    """Check prereqs and coreqs for all TU courses in student's plan;
    results returned as two lists of id #s"""
    studentdata = Student.objects.all().filter(pk=studentid)
    student = studentdata[0]
    sscdata = StudentSemesterCourses.objects.all().filter(student=student)
    cyocdata = CreateYourOwnCourse.objects.all().filter(student=student)

    enteringyear = student.entering_year
    courselist = []
    courseiddict=dict()
    semesterdict=dict()
    for ssc in sscdata:
        sscid = ssc.id
        actualyear = ssc.actual_year
        semester = ssc.semester
        semestersincebeginning = get_semester_from_beginning(enteringyear, actualyear, semester)
        semesterdict[semestersincebeginning]=sscid
        for course in ssc.courses.all():
            courseiddict[course.id]=course.number
            prereq = []
            coreq = []
            for pre in course.prereqs.all():
                prereq.append(pre.id)
                courseiddict[pre.id]=pre.number
            for co in course.coreqs.all():
                coreq.append(co.id)
                courseiddict[co.id]=co.number
            courselist.append([semestersincebeginning, actualyear, semester, course.id, prereq, coreq, sscid])

    # Now in add in "create your own" type courses that have exact equivalents at TU....
    # note: in the way I have done this, it is assumed that the course functions exactly
    # as a TU course; that is, it has the same prereqs and coreqs, it satisfies prereqs
    # and coreqs, etc.
    for cyoc in cyocdata:
        if cyoc.equivalentcourse is not None:
            semester = cyoc.semester
            actualyear = cyoc.actual_year
            semestersincebeginning = get_semester_from_beginning(enteringyear, actualyear, semester)
            sscid = semesterdict[semestersincebeginning]
            prereq = []
            coreq = []
            course = cyoc.equivalentcourse
            courseiddict[course.id]=course.number
            for pre in course.prereqs.all():
                prereq.append(pre.id)
                courseiddict[pre.id]=pre.number
            for co in course.coreqs.all():
                coreq.append(co.id)
                courseiddict[co.id]=co.number
            courselist.append([semestersincebeginning, actualyear, semester, course.id, prereq, coreq, sscid])

    # Now need to do the actual check....
    allprelist=[]
    allcolist=[]
    prenotmetlist=[]
    conotmetlist=[]
    courselist2=courselist
    for row in courselist:
        coursesemester = row[0]
        # Don't do prereq and coreq check for pre-TU courses, although pre-TU courses can
        # be pre and coreqs for OTHER courses
        if coursesemester != 0:
            prereqlist = row[4]
            coreqlist = row[5]
            sscid = row[6]
            courseid = row[3]
            # Now for each preid, need to find the semester that that course was taken,
            # check that it was earlier than course itself
            for preid in prereqlist:
                prereqsatisfied = False
                for row2 in courselist2:
                    courseidtemp = row2[3]
                    coursesemesterpre = row2[0]
                    if courseidtemp==preid and coursesemesterpre<coursesemester:
                        prereqsatisfied = True
                        allprelist.append([courseiddict[courseid],courseiddict[preid]])
                if prereqsatisfied == False:
                    prenotmetlist.append([sscid, courseid, courseiddict[courseid],
                                          preid, courseiddict[preid]])
            # Now for each coid, need to find the semester that that course was taken,
            # check that it was <= than semester for course itself
            for coid in coreqlist:
                coreqsatisfied = False
                for row2 in courselist2:
                    courseidtemp = row2[3]
                    coursesemesterco = row2[0]
                    if courseidtemp==coid and coursesemesterco<=coursesemester:
                        coreqsatisfied = True
                        allcolist.append([courseiddict[courseid],courseiddict[coid]])
                if coreqsatisfied == False:
                    conotmetlist.append([sscid,courseid,courseiddict[courseid],
                                         coid,courseiddict[coid]])

    return prenotmetlist, conotmetlist

def get_semester_from_beginning(enteringyear, actualyear, semester):
    """Return semester #, starting with "0" for pre-TU, "1" for freshman fall, etc."""
    if semester == 0:
        semesteroutput = 0
    else:
        if semester == 1:
            semesteroutput = 4 * (actualyear - enteringyear) + semester
        else:
            semesteroutput = 4 * (actualyear - enteringyear - 1) + semester
    return semesteroutput

def named_year(enteringyear, actualyear, semester):
    termdict = {1: "fall", 2: "j-term", 3: "spring", 4: "summer"}
    yeardict = {0: "freshman", 1: "sophomore", 2: "junior", 3: "senior", 4: "supersenior"}
    if semester == 1:
        yeardiff = actualyear - enteringyear
    else:
        yeardiff = actualyear - enteringyear - 1
    return yeardict[yeardiff]+' '+termdict[semester]+' ('+str(actualyear)+')'

# list is assumed to be of the form:
#     - [[year, sem, id],[year, sem, id],...]; or
#     - [[year, sem, id, numcrhrssem],[year, sem, id, numcrhrssem],...]
def reorder_list(listin):
    alphdict={2:'a', 3:'b', 4:'c', 1:'d'}
    revalphdict={'a':2, 'b':3, 'c':4, 'd':1}
    newlist=[]
    for row in listin:
        if len(row) == 4:
            newlist.append([row[0],alphdict[row[1]],row[2], row[3]])
        else:
            newlist.append([row[0],alphdict[row[1]],row[2]])
    newlist2=sorted(newlist, key=lambda rrow: (rrow[0], rrow[1]))
    newlist3=[]
    for row in newlist2:
        if len(row) == 4:
            newlist3.append([row[0],revalphdict[row[1]],row[2], row[3]])
        else:
            newlist3.append([row[0],revalphdict[row[1]],row[2]])
    return newlist3

def prepopulate_student_semesters(studentid):
    student = Student.objects.all().get(pk = studentid)
    major = student.major
    enteringyear=student.entering_year
    datalist = PrepopulateSemesters.objects.all().filter(Q(major=major)&Q(enteringyear__year=enteringyear))
    tempdata=StudentSemesterCourses.objects.all().filter(student=student)
    ssclist=[]
    for ssc in tempdata:
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
                    courseid = course.id
                    StudentSemesterCourses.objects.get(pk = sscid).courses.add(courseid)

    return True

# In the following, "wherefrom" is:
# 0: profile
# 1: fouryearplan
# 2: graduaudit
# 3: advising note
@login_required
def update_advisee(request, wherefrom):
    if request.user.is_student():
        return redirect('profile')

    professor = request.user.professor

    if request.method == 'POST':
        form = AddAdviseeForm(request.POST, instance=professor)
        if form.is_valid():
            form.save()
            if int(wherefrom) == 0:
                return redirect('profile')
            elif int(wherefrom) == 1:
                return redirect('four_year_plan')
            elif int(wherefrom) == 2:
                return redirect('grad_audit')
            elif int(wherefrom) == 3:
                return redirect('advising_notes')
            else:
                return redirect('profile')
        else:
            return render(request, 'addadvisee.html', {'form': form})
    else:
        # User is not submitting the form; show them the blank add advisee form
        form = AddAdviseeForm()
        context = {'form': form}
        return render(request, 'addadvisee.html', context)

# PUT in something to limit search results!!!!  maybe only display first 20 records or
# something!!!  !!! do we need to do any security stuff here to make sure this is really a
# prof?!?
@login_required
def search(request):
    """Determine the # of students enrolled in courses that match a search request."""

    # check if the "professor" is actually a professor....
    professor = request.user.get_profile

    temp = Professor.objects.all().filter(user=professor)

    if len(temp) == 0: # this is a student, not a professor
        return redirect('profile')
    if 'q' in request.GET and request.GET['q']:
        q = request.GET['q']
        courses = Course.objects.filter(number__icontains=q)
        semesterdict = {1:"Fall", 2:"J-term", 3:"Spring", 4:"Summer"}
        datablock = []
        for course in courses:
            semlist = []

            # This approach is only going to capture non-pre-TU courses...which is good.
            for availablesemester in course.semester.all():
                actualsem = availablesemester.semester_of_acad_year
                actualyear = availablesemester.actual_year

                # Now need to find all the ssc records for each of these courses....
                sscdata = StudentSemesterCourses.objects.filter(semester=actualsem)
                numberstudents=0
                studentlist=[]
                for ssc in sscdata:
                    if ssc.actual_year == actualyear:
                        for courseinssc in ssc.courses.all():
                            if courseinssc.id == course.id:
                                numberstudents=numberstudents + 1
                                studentlist.append(ssc.student.name)
                semlist.append([actualyear, actualsem, numberstudents,availablesemester.id])
            semlist2 = reorder_list(semlist)
            semlistfinal = []
            for row in semlist2:
                semlistfinal.append([semesterdict[row[1]] + ", " + str(row[0]),row[2], row[3]])
            datablock.append([course.id, course.name, course.number, semlistfinal])
        context={'courses':courses,'query':q, 'datablock':datablock}
        return render(request, 'course_enrollment_results.html',context)
    else:
        return redirect('profile')


@login_required
def view_enrolled_students(request,courseid,semesterid):
    """Display students enrolled in a given course and semester"""

    # Check if the "professor" is actually a professor....
    professor = request.user.get_profile

    temp = Professor.objects.all().filter(user=professor)

    if len(temp) == 0: # this is a student, not a professor
        return redirect('profile')

    actualsem = Semester.objects.get(pk=semesterid).semester_of_acad_year
    actualyear = Semester.objects.get(pk=semesterid).actual_year
    sscdata = StudentSemesterCourses.objects.filter(semester=actualsem)
    course = Course.objects.get(pk=courseid)
    coursename = course.name + ' (' + course.number + ')'
    semesterdict = {1:"Fall", 2:"J-term", 3:"Spring", 4:"Summer"}
    semestername = semesterdict[actualsem] + ' of ' + str(actualyear)
    studentlist=[]
    for ssc in sscdata:
        if ssc.actual_year == actualyear:
            for courseinssc in ssc.courses.all():
                if courseinssc.id == int(courseid):
                    studentlist.append(ssc.student.name)
    temp = request.META.items()
    context={'coursename':coursename,'semestername':semestername,'studentlist':studentlist}
    return render(request, 'student_enrollment_results.html', context)
