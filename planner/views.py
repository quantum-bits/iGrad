from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
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
        if form.is_valid():
            user = User.objects.create_user(username = form.cleaned_data['username'],
                                            email = form.cleaned_data['email'],
                                            password = form.cleaned_data['password'])
            user.save()

            student = Student(user=user,
                              name=form.cleaned_data['name'],
                              entering_year=form.cleaned_data['entering_year'],
                              major = form.cleaned_data['major'])
            student.save()

            yearlist = [0, 1, 2, 3, 4, 5]
            semesterlist = [1, 2, 3, 4]
            for year_temp in yearlist:
                if year_temp == 0:
                    semester_temp = 0
                    p1 = StudentSemesterCourses(student=student,
                                                year=year_temp,
                                                semester=semester_temp)
                    p1.save()
                else:
                    for semester_temp in semesterlist:
                        p1 = StudentSemesterCourses(student=student,
                                                    year=year_temp,
                                                    semester=semester_temp)
                        p1.save()

            if student.major is not None:
                courses_added = prepopulate_student_semesters(student.id)
            else:
                courses_added = False

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
    user = request.user

    if user.is_student():
        isProfessor = False
        professorname = ''
        advisee = None
    else:
        isProfessor = True
        professorname = user.professor.name
        advisee = user.professor.advisee

    # Note: to access the email address in the view, you could set it to
    # email = student.user.email
    context = { 'isProfessor': isProfessor,
                'professorname': professorname,
                'advisee': advisee }
    return render(request, 'profile.html', context)

@login_required
def update_major(request, id):
    request_id = request.user.get_student_id()
    incoming_id = int(id)

    if request_id != incoming_id:
        return redirect('profile')

    instance = Student.objects.get(pk=id)

    if request.method == 'POST':
        form = UpdateMajorForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('profile')
        else:
            return render(request, 'updatemajor.html', {'form': form})
    else:
        # User is not submitting the form; show them the blank add major form.
        form = UpdateMajorForm(instance=instance)
        context = {'form': form}
        return render(request, 'updatemajor.html', context)


# problems: 
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
    request_id = request.user.get_student_id()
    incoming_id = instance.student.id
    if request_id != incoming_id:
        return redirect('profile')

    year = instance.actual_year
    semester = instance.semester
    student_local = request.user
    student_created_courses = CreateYourOwnCourse.objects.all().filter(Q(student=student_local) &
                                                                       Q(semester=semester) &
                                                                       Q(actual_year=year))
    courselist= Course.objects.filter(Q(sospring=1) & Q(semester__actual_year=year) & Q(semester__semester_of_acad_year = semester))
    current_course_list = Course.objects.filter(Q(semester__actual_year=year) & Q(semester__semester_of_acad_year = semester))

    sccdatablock=[]
    for scc in student_created_courses:
        if scc.equivalentcourse:
            eqnum = ", equiv to " + scc.equivalentcourse.number
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
        my_kwargs = dict(instance=instance,
                         actual_year=year,
                         semester=semester)
        form = AddStudentSemesterForm(request.POST, **my_kwargs)
        if form.is_valid():
            form.save()
            return redirect('four_year_plan')
        else:
            return render(request, 'updatesemester.html',
                          {'form': form, 'sccdatablock':sccdatablock})
    else:
        # User is not submitting the form; show them the blank add semester form.
        my_kwargs = dict(instance=instance,
                         actual_year=year,
                         semester=semester)
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
            return redirect('update_advisee', 3)

    temp_data = AdvisingNote.objects.all().filter(student=student_local)

    datablock = []
    ii = 0
    for adv_notes in temp_data:
        ii = ii + 1
        datablock.append([adv_notes.datestamp, adv_notes.note, adv_notes.id, ii])

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
            return redirect('advising_notes')
        else:
            return render(request, 'addAdvisingNote.html', {'form': form})
    else:
        # user is not submitting the form; show them the blank add semester form
        form = AddAdvisingNoteForm()
        context = {'form': form}
        return render(request, 'addAdvisingNote.html', context)


@login_required
def update_advising_note(request, id):
    instance = AdvisingNote.objects.get(pk = id)
    request_id = request.user.get_student_id()
    incoming_id = instance.student.id
    if request_id != incoming_id:
        return redirect('profile')

    if request.method == 'POST':
        form = AddAdvisingNoteForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('advising_notes')
        else:
            return render(request, 'addAdvisingNote.html', {'form': form})
    else:
        # user is not submitting the form; show them the blank add semester form
        form = AddAdvisingNoteForm(instance=instance)
        context = {'form': form}
        return render(request, 'addAdvisingNote.html', context)

@login_required
def delete_advising_note(request, id):
    instance = AdvisingNote.objects.get(pk = id)
    request_id = request.user.get_student_id()
    incoming_id = instance.student.id
    if request_id != incoming_id:
        return redirect('profile')

    instance.delete()
    return redirect('advising_notes')

@login_required
def display_four_year_plan(request):
    print request.user.is_student()
    if request.user.is_student():
        isProfessor = False
        student_local = request.user.student
    else:
        isProfessor = True
        student_local = request.user.professor.advisee
        if student_local is None:
            # No advisee currently selected; go pick one first.
            return redirect('update_advisee', 1)

    total_credit_hours_four_years = 0
    temp_data = StudentSemesterCourses.objects.all().filter(student=student_local)
    temp_data2 = CreateYourOwnCourse.objects.all().filter(student=student_local)

    enteringyear = temp_data[0].student.entering_year

    studentid = temp_data[0].student.id
    pre_not_met_list, co_not_met_list = pre_co_req_check(studentid)

    # ssclist is used for later on when we try to find other semesters that a given course
    # is offered.
    ssclist=[]
    for ssc in temp_data:
        if ssc.semester !=0:
            # Don't include pre-TU ssc object here
            numcrhrsthissem = 0
            for course in ssc.courses.all():
                numcrhrsthissem = numcrhrsthissem + course.credit_hours
            # Now add in credit hours from any create your own type courses
            temp_data4 = temp_data2.filter(Q(semester=ssc.semester)&Q(actual_year=ssc.actual_year))
            for course in temp_data4:
                numcrhrsthissem = numcrhrsthissem + course.credit_hours
            ssclist.append([ssc.id, ssc.actual_year, ssc.semester, numcrhrsthissem])

    termdictionaryalphabetize={0:"aPre-TU", 1:"eFall", 2:"bJ-term", 3:"cSpring", 4:"dSummer"}
    termdictionary={0:"Pre-TU", 1:"Fall", 2:"J-term", 3:"Spring", 4:"Summer"}

    # First, form an array containing the info for the "create your own" type courses
    cyocarray=[]
    for cyoc in temp_data2:
        if cyoc.equivalentcourse:
            equivcourse_namestring = ' (equivalent to: '+cyoc.equivalentcourse.number+')'
        else:
            equivcourse_namestring =''
        cyocarray.append([cyoc.actual_year, termdictionaryalphabetize[cyoc.semester],
                          cyoc.name+equivcourse_namestring,
                          cyoc.number, cyoc.credit_hours, cyoc.sp, cyoc.cc, cyoc.id])

    datablock=[]
    # "Alphabetize" the semesters.
    for sem1 in temp_data:
        semestercontainscyoc = False
        temp_course_name=[]
        semtemp = sem1.semester
        act_year_temp = sem1.actual_year
        semid = sem1.id
        total_credit_hrs = 0
        tempcyocarray =[]
        ii = 0
        # Assemble any prereq or coreq comments into a list....
        precocommentlist=[]
        for row in co_not_met_list:
            if row[0] == semid:
                precocommentlist.append(row[4] + " is a corequisite for " +
                                        row[2] + "; the requirement is currently not being met.")
        for row in pre_not_met_list:
            if row[0] == semid:
                precocommentlist.append(row[4] + " is a prerequisite for " +
                                        row[2] + "; the requirement is currently not being met.")
        for row in cyocarray:
            if row[0] == act_year_temp and row[1] == termdictionaryalphabetize[semtemp]:
                tempcyocarray.append(ii)
            ii=ii+1
        for indexii in reversed(tempcyocarray):
            temparray = cyocarray.pop(indexii)
            total_credit_hrs = total_credit_hrs+temparray[4]
            iscyoc = True
            semestercontainscyoc = True
            temp_course_name.append({'cname': temparray[2],
                                   'cnumber': temparray[3],
                                   'ccredithours': temparray[4],
                                   'sp': temparray[5],
                                   'cc': temparray[6],
                                   'iscyoc': iscyoc,
                                   'courseid': temparray[7],
                                   'othersemesters': []})
        for cc in sem1.courses.all():
            iscyoc = False
            total_credit_hrs = total_credit_hrs + cc.credit_hours
            allsemestersthiscourse = cc.semester.all()
            # Form an array of other semesters when this course is offered.
            semarraynonordered = []
            for semthiscourse in allsemestersthiscourse:
                yearotheroffering=semthiscourse.actual_year
                semotheroffering=semthiscourse.semester_of_acad_year
                keepthisone = True
                if yearotheroffering == act_year_temp and semotheroffering == semtemp:
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

            temp_course_name.append({'cname': cc.name,
                                   'cnumber': cc.number,
                                   'ccredithours': cc.credit_hours,
                                   'sp': cc.sp,
                                   'cc': cc.cc,
                                   'iscyoc': iscyoc,
                                   'courseid': cc.id,
                                   'othersemesters':semarray})
        datablock.append({'year': act_year_temp,
                          'semestername': termdictionaryalphabetize[semtemp],
                          'studentname': sem1.student.name,
                          'listofcourses': temp_course_name,
                          'semesterid': sem1.id,
                          'totalcredithours': total_credit_hrs,
                          'semestercontainscyoc': semestercontainscyoc,
                          'precocommentlist': precocommentlist})
        total_credit_hours_four_years = total_credit_hours_four_years + total_credit_hrs

    # initial sort
    datablock2 = sorted(datablock, key=lambda rrow: (rrow['year'], rrow['semestername']))
    datablock3 = []
    for row in datablock2:
        row['semestername'] = row['semestername'][1:]
        datablock3.append(row)

    if total_credit_hours_four_years > 159:
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
               'totalhrsfouryears': total_credit_hours_four_years,
               'credithrmaxreached': credithrmaxreached,
               'isProfessor': isProfessor}
    return render(request, 'fouryearplan.html', context)

@login_required
def display_grad_audit(request):
    # NOTES: 
    #       1. In the current approach no double-counting of courses is allowed, since the course gets popped
    #          out of studentcourselist as soon as it meets a requirement.  Maybe this should be changed?  The problem
    #          could be that in some situations, maybe a course is not ALLOWED to double-count.  Maybe if one course
    #          is used to meet requirements in two requirement blocks, a flag could be set and a warning given, in case
    #          such double-counting is not allowed.
    #       2. There is some redundancy between this function and display_four_year_plan.  Some methods/functions could 
    #          probably be written that would serve in both places

    if request.user.is_student():
        isProfessor = False
        student_local = request.user.student
    else:
        isProfessor = True
        student_local = request.user.professor.advisee
        if student_local is None:
            # No advisee currently selected; go pick one first
            return redirect('update_advisee', 2)

    temp_data = StudentSemesterCourses.objects.all().filter(student=student_local)
    temp_data3 = CreateYourOwnCourse.objects.all().filter(student=student_local)

    studentid = temp_data[0].student.id
    pre_not_met_list, co_not_met_list = pre_co_req_check(studentid)

    if student_local.major is None:
        hasMajor = False
        context = {'student': student_local,'isProfessor': isProfessor,'hasMajor':hasMajor}
        return render(request, 'graduationaudit.html', context)
    else:
        hasMajor = True
        studentmajor = student_local.major

    enteringyear = student_local.entering_year

#
# OVERVIEW of majordatablock:
#
# one of the main tasks performed here is to construct "majordatablock";
# "majordatablock" is a list of dictionaries that is eventually reordered and renamed "majordatablock2";
# aside from the reordering, these two lists are identical.
# majordatablock2 is *the* main chunk of data that is sent to the graduationaudit template.
#
# each element in the list (majordatablock) is a "requirement block"; 
# the requirement blocks have the following keywords:
#
#  - listorder: an integer used to determine what order the requirements should be displayed in
#  - blockname: the name of the requirement block; this will show up on the grad audit page
#  - andorcomment: string that states whether all or only some of the courses need to be taken 
#  - mincredithours: minimum # of credit hours to satisfy the requirement
#  - textforuser: optional text to display to the user
#  - credithrs: total # credit hours in this block so far
#  - creditsok: whether or not the # credit hours taken so far matches the required number
#  - blockcontainscyoc: whether or not the requirement block currently contains a course that is 
#                       of the "create your own" variety; if so, a not is put at the bottom
#  - precocommentlist: list of comments about prereqs or coreqs not being met, if that is the case
#  - courselist: list of dictionaries; each element in the list represents a course
#                keywords are the following:
#      - cname: course name
#      - cnumber: course number (e.g., PHY311)
#      - ccredithrs': # credit hours required for this course requirement
#      - sp: boolean 
#      - cc: boolean 
#      - comment: comment to be associated with the course
#      - numcrhrstaken: # of credit hours taken for this requirement
#      - courseid: course id in the database
#      - sscid: id of the studentsemestercourse object associated with this course
#      - iscyoc: boolean; TRUE if the course is of the "create your own" variety
#      - othersemester: list of dictionaries; each element represents another
#                       semester during which this course could be taken; 
#                       keywords are the following:
#           - semester: string that identifies the other semester (e.g., 'junior spring (2015)')
#           - courseid: *poorly named*; actually the id of the studentsemestercourse object for the course in the other semester
#           - numhrsthissem: # credit hrs currently being taken in the other semester
#

    # ssclist is used below to construct "semarray", which is eventually assigned to the keyword "othersemester" (see above)
    ssclist=[]
    for ssc in temp_data:
        if ssc.semester !=0:  # don't include pre-TU ssc object here
            numcrhrsthissem = student_local.num_credit_hours(ssc)
            ssclist.append([ssc.id, ssc.actual_year, ssc.semester, numcrhrsthissem])

    termdictionary={0:"Pre-TU", 1:"Fall", 2:"J-term", 3:"Spring", 4:"Summer"}

    # the following assembles studentcourselist and coursenumberlist;
    # studentcourselist is a list of all courses in the student's plan;
    # elements in the list correspond to information about the courses (name, semester, etc.)
    # coursenumberlist is a parallel list to studentcourselist, but it just contains course numbers (e.g., PHY311)
    studentcourselist=[]
    coursenumberlist=[]
    # In the next line of code I use "len()" in order to force django to evaluate the
    # QuerySet...otherwise I get an error saying that the "ManyRelatedManager object is
    # not iterable"
    numrecords=len(temp_data)
    # loop through all studentsemestercourse objects for the student, picking out the courses in the student's plan
    for ssc in temp_data:
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
    for cyoc in temp_data3:
        iscyoc = True
        if cyoc.equivalentcourse:
            equivcourse_namestring = ' (equivalent to: '+cyoc.equivalentcourse.number+')'
            eqcoursenum = cyoc.equivalentcourse.number
        else:
            equivcourse_namestring =''
            eqcoursenum = ''
        studentcourselist.append([cyoc.name+equivcourse_namestring,
                                  cyoc.semester,
                                  cyoc.actual_year,
                                  cyoc.credit_hours,
                                  cyoc.sp,
                                  cyoc.cc,
                                  iscyoc,
                                  cyoc.number,
                                  cyoc.id])
        coursenumberlist.append(eqcoursenum)

    # the following assembles SPlist and CClist; these lists contain information about
    # SP and CC courses in the student's plan and are passed directly to the template

    SPlist=[]
    CClist=[]
    numSPs=0
    numCCs=0
    ii=0
    total_credit_hours_four_years=0
    for course in studentcourselist:
        total_credit_hours_four_years=total_credit_hours_four_years+course[3]
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

    # the following code assembles majordatablock (described in detail above);
    # the general approach is the following:
    # - the outer loop cycles through each requirement block for the student's major
    #   - the next loop cycles through each course in the list of courses within the requirement block
    #   - if a course in the student's plan ("studentcourselist") matches a course in a requirement block, it is 
    #     popped out of the student's course list
    #   - for most courses in the requirement block, a list of semesters is constructed, showing when the course
    #     could be taken (or moved to, if it is currently being taken during some semester)

    majordatablock = []
    # loop over requirement blocks for the student's chosen major
    for mr in studentmajor.major_requirements.all():
        precocommentlist=[]
        requirementblockcontainscyoc = False
        courselisttemp=[]
        if mr.AND_or_OR_Requirement == 1:
            AND_OR_comment = "All of the following are required."
        else:
            AND_OR_comment = "Choose from the following."
        total_credit_hours_so_far=0
        course_id_list=[]
        # loop over courses within each requirement block
        for course in mr.courselist.all():
            iscyoc=False
            cnumber=course.number
            course_id = course.id
            course_id_list.append(course_id)
            numcrhrstaken = ''
            sscid = -1
            try:
                ii=coursenumberlist.index(cnumber)
            except ValueError:
                ii=-1
            # if the requirement is met, pop the course out of the student's list of courses
            if ii !=-1:
                # Assemble any prereq or coreq comments into a list.
                for row in co_not_met_list:
                    if row[1] == course_id:
                        precocommentlist.append(row[4] + " is a corequisite for " +
                                                row[2] + "; the requirement is currently not being met.")
                for row in pre_not_met_list:
                    if row[1] == course_id:
                        precocommentlist.append(row[4] + " is a prerequisite for " +
                                                row[2] + "; the requirement is currently not being met.")
                courseinfo=studentcourselist.pop(ii)
                cnumbertemp=coursenumberlist.pop(ii)
                numcrhrstaken = courseinfo[3]
                total_credit_hours_so_far+=numcrhrstaken
                semtemp = courseinfo[1]
                act_year_temp = courseinfo[2]
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
                act_year_temp = -1

            # If course is user-defined ("cyoc"), then don't show options for moving the
            # course, so skip the next part
            if iscyoc:
                semarray = []
            # if the course is a regular course, assemble a list of possible semesters to take the course
            else:
                allsemestersthiscourse = course.semester.all()

                # Form an array of other semesters when this course is offered.
                semarraynonordered = []

                for semthiscourse in allsemestersthiscourse:
                    yearotheroffering=semthiscourse.actual_year
                    semotheroffering=semthiscourse.semester_of_acad_year
                    keepthisone = True
                    if yearotheroffering == act_year_temp and semotheroffering == semtemp:
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

        # the following appends a new dictionary for this particular requirement block
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

        # the following reorders majordatablock in the desired order 
        # (this ordering is defined when the requirement blocks are defined in the first place)
        majordatablock2 = sorted(majordatablock, key=lambda rrow: (rrow['listorder']))

        # anything remaining in the studentcourselist at this point has not been used to meet a 
        # course requirement in one of the requirement blocks;  unusedcourses keeps track of these courses
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
        # the following checks to see if the SP and CC requirements have been met
        if numSPs < 2:
            SPreq = False
        else:
            SPreq = True
        if numCCs == 0:
            CCreq = False
        else:
            CCreq = True

    if total_credit_hours_four_years > 159:
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
               'totalhrsfouryears': total_credit_hours_four_years,
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
            return redirect('advising_notes')
        else:
            return render(request, 'addAdvisingNote.html', {'form': form})
    else:
        # User is not submitting the form; show them the blank add semester form
        form = AddAdvisingNoteForm()
        context = {'form': form}
        return render(request, 'addAdvisingNote.html', context)

@login_required
def add_create_your_own_course(request,id):
    # The following list should just have one element(!)...hence "listofstudents[0]" is
    # used in the following....
    listofstudents = Student.objects.all().filter(user=request.user)
    ssc = StudentSemesterCourses.objects.get(pk = id)
    request_id = request.user.get_student_id()
    incoming_id = ssc.student.id
    if request_id != incoming_id:
        return redirect('profile')
    year=ssc.actual_year
    semester=ssc.semester

    if request.method == 'POST':
        form = AddCreateYourOwnCourseForm(request.POST)
        if form.is_valid():
            new_cyoc = CreateYourOwnCourse(student = listofstudents[0])
            new_cyoc.name = form.cleaned_data['name']
            new_cyoc.number = form.cleaned_data['number']
            new_cyoc.credit_hours = form.cleaned_data['credit_hours']
            new_cyoc.sp = form.cleaned_data['sp']
            new_cyoc.cc = form.cleaned_data['cc']
            new_cyoc.semester = semester
            new_cyoc.actual_year = year
            new_cyoc.equivalentcourse = form.cleaned_data['equivalentcourse']
            new_cyoc.save()
            return redirect('update_student_semester', id)
        else:
            return render(request, 'addcreateyourowncourse.html', {'form': form})
    else:
        # User is not submitting the form; show them the blank add create your own course
        # form.
        form = AddCreateYourOwnCourseForm()
        context = {'form': form}
        return render(request, 'addcreateyourowncourse.html', context)


@login_required
def update_create_your_own_course(request,id,id2):
    instance = CreateYourOwnCourse.objects.get(pk = id2)
    ssc = StudentSemesterCourses.objects.get(pk = id)
    request_id = request.user.get_student_id()
    incoming_id = ssc.student.id
    incoming_id2 = instance.student.id
    if request_id != incoming_id:
        return redirect('profile')
    if request_id != incoming_id2:
        return redirect('profile')

    if request.method == 'POST':
        form = AddCreateYourOwnCourseForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('update_student_semester', id)
        else:
            return render(request, 'addcreateyourowncourse.html', {'form': form})
    else:
        # User is not submitting the form; show them the blank add create your own course form
        form = AddCreateYourOwnCourseForm(instance=instance)
        context = {'form': form}
        return render(request, 'addcreateyourowncourse.html', context)


# In the following, "where_from" is:
#    0: fouryearplan
#    1: gradaudit
#    2: updatesemester
# "id" is:
#    0: coming from fouryearplan (doesn't matter; not used)
#    0: coming from gradaudit (doesn't matter; not used)
#    ssc id: coming from updatesemester
@login_required
def delete_create_your_own_course(request, where_from, id, id2):
    instance = CreateYourOwnCourse.objects.get(pk = id2)

    request_id = request.user.get_student_id()
    incoming_id2 = instance.student.id
    if request_id != incoming_id2:
        return redirect('profile')

    instance.delete()
    if int(where_from) == 2:
        return redirect('update_student_semester', id)
    elif int(where_from) == 0:
        return redirect('four_year_plan')
    else:
        return redirect('grad_audit')

# In the following, where_from is:
#    0: fouryearplan
#    1: gradaudit
# ssc_id is id of the ssc object
# course_id is id of the course itself
@login_required
def delete_course_inside_SSCObject(request, where_from, ssc_id, course_id):
    instance = StudentSemesterCourses.objects.get(pk = ssc_id)

    request_id = request.user.get_student_id()
    incoming_id = instance.student.id
    if request_id != incoming_id:
        return redirect('profile')

    StudentSemesterCourses.objects.get(pk = ssc_id).courses.remove(course_id)
    if int(where_from) == 0:
        return redirect('four_year_plan')
    else:
        return redirect('grad_audit')

# In the following, where_from is:
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
def move_course_to_new_SSCObject(request, where_from, src_ssc_id, dest_ssc_id, course_id):
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
    if int(where_from) == 0:
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
    course_id_dict=dict()
    semesterdict=dict()
    for ssc in sscdata:
        sscid = ssc.id
        actual_year = ssc.actual_year
        semester = ssc.semester
        semestersincebeginning = get_semester_from_beginning(enteringyear, actual_year, semester)
        semesterdict[semestersincebeginning]=sscid
        for course in ssc.courses.all():
            course_id_dict[course.id]=course.number
            prereq = []
            coreq = []
            for pre in course.prereqs.all():
                prereq.append(pre.id)
                course_id_dict[pre.id]=pre.number
            for co in course.coreqs.all():
                coreq.append(co.id)
                course_id_dict[co.id]=co.number
            courselist.append([semestersincebeginning, actual_year, semester, course.id, prereq, coreq, sscid])

    # Now in add in "create your own" type courses that have exact equivalents at TU....
    # note: in the way I have done this, it is assumed that the course functions exactly
    # as a TU course; that is, it has the same prereqs and coreqs, it satisfies prereqs
    # and coreqs, etc.
    for cyoc in cyocdata:
        if cyoc.equivalentcourse is not None:
            semester = cyoc.semester
            actual_year = cyoc.actual_year
            semestersincebeginning = get_semester_from_beginning(enteringyear, actual_year, semester)
            sscid = semesterdict[semestersincebeginning]
            prereq = []
            coreq = []
            course = cyoc.equivalentcourse
            course_id_dict[course.id]=course.number
            for pre in course.prereqs.all():
                prereq.append(pre.id)
                course_id_dict[pre.id]=pre.number
            for co in course.coreqs.all():
                coreq.append(co.id)
                course_id_dict[co.id]=co.number
            courselist.append([semestersincebeginning, actual_year, semester, course.id, prereq, coreq, sscid])

    # Now need to do the actual check....
    all_pre_list = []
    all_co_list = []
    pre_not_met_list = []
    co_not_met_list = []
    courselist2=courselist
    for row in courselist:
        coursesemester = row[0]
        # Don't do prereq and coreq check for pre-TU courses, although pre-TU courses can
        # be pre and coreqs for OTHER courses
        if coursesemester != 0:
            prereq_list = row[4]
            coreq_list = row[5]
            sscid = row[6]
            course_id = row[3]
            # Now for each preid, need to find the semester that that course was taken,
            # check that it was earlier than course itself
            for preid in prereq_list:
                prereqsatisfied = False
                for row2 in courselist2:
                    course_idtemp = row2[3]
                    coursesemesterpre = row2[0]
                    if course_idtemp==preid and coursesemesterpre<coursesemester:
                        prereqsatisfied = True
                        all_pre_list.append([course_id_dict[course_id],course_id_dict[preid]])
                if prereqsatisfied == False:
                    pre_not_met_list.append([sscid, course_id, course_id_dict[course_id],
                                          preid, course_id_dict[preid]])
            # Now for each coid, need to find the semester that that course was taken,
            # check that it was <= than semester for course itself
            for coid in coreq_list:
                coreqsatisfied = False
                for row2 in courselist2:
                    course_idtemp = row2[3]
                    coursesemesterco = row2[0]
                    if course_idtemp==coid and coursesemesterco<=coursesemester:
                        coreqsatisfied = True
                        all_co_list.append([course_id_dict[course_id],course_id_dict[coid]])
                if coreqsatisfied == False:
                    co_not_met_list.append([sscid,
                                            course_id,
                                            course_id_dict[course_id],
                                            coid,
                                            course_id_dict[coid]])

    return pre_not_met_list, co_not_met_list

def get_semester_from_beginning(enteringyear, actual_year, semester):
    """Return semester #, starting with "0" for pre-TU, "1" for freshman fall, etc."""
    if semester == 0:
        semesteroutput = 0
    else:
        if semester == 1:
            semesteroutput = 4 * (actual_year - enteringyear) + semester
        else:
            semesteroutput = 4 * (actual_year - enteringyear - 1) + semester
    return semesteroutput

def named_year(enteringyear, actual_year, semester):
    termdict = {1: "fall", 2: "j-term", 3: "spring", 4: "summer"}
    yeardict = {0: "freshman", 1: "sophomore", 2: "junior", 3: "senior", 4: "supersenior"}
    if semester == 1:
        yeardiff = actual_year - enteringyear
    else:
        yeardiff = actual_year - enteringyear - 1
    return yeardict[yeardiff]+' '+termdict[semester]+' ('+str(actual_year)+')'

# list is assumed to be of the form:
#     - [[year, sem, id],[year, sem, id],...]; or
#     - [[year, sem, id, numcrhrssem],[year, sem, id, numcrhrssem],...]
def reorder_list(listin):
    alphdict={2:'a', 3:'b', 4:'c', 1:'d'}
    revalphdict={'a':2, 'b':3, 'c':4, 'd':1}
    new_list=[]
    for row in listin:
        if len(row) == 4:
            new_list.append([row[0],alphdict[row[1]],row[2], row[3]])
        else:
            new_list.append([row[0],alphdict[row[1]],row[2]])
    new_list2=sorted(new_list, key=lambda rrow: (rrow[0], rrow[1]))
    new_list3=[]
    for row in new_list2:
        if len(row) == 4:
            new_list3.append([row[0],revalphdict[row[1]],row[2], row[3]])
        else:
            new_list3.append([row[0],revalphdict[row[1]],row[2]])
    return new_list3

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

# In the following, "where_from" is:
# 0: profile
# 1: fouryearplan
# 2: graduaudit
# 3: advising note
@login_required
def update_advisee(request, where_from):
    if request.user.is_student():
        return redirect('profile')

    professor = request.user.professor

    if request.method == 'POST':
        form = AddAdviseeForm(request.POST, instance=professor)
        if form.is_valid():
            form.save()
            if int(where_from) == 0:
                return redirect('profile')
            elif int(where_from) == 1:
                return redirect('four_year_plan')
            elif int(where_from) == 2:
                return redirect('grad_audit')
            elif int(where_from) == 3:
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

    if request.user.is_student():
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
                actual_sem = availablesemester.semester_of_acad_year
                actual_year = availablesemester.actual_year

                # Now need to find all the ssc records for each of these courses....
                sscdata = StudentSemesterCourses.objects.filter(semester=actual_sem)
                numberstudents=0
                studentlist=[]
                for ssc in sscdata:
                    if ssc.actual_year == actual_year:
                        for courseinssc in ssc.courses.all():
                            if courseinssc.id == course.id:
                                numberstudents=numberstudents + 1
                                studentlist.append(ssc.student.name)
                semlist.append([actual_year, actual_sem, numberstudents,availablesemester.id])
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
def view_enrolled_students(request,course_id,semesterid):
    """Display students enrolled in a given course and semester"""

    if request.user.is_student():
        return redirect('profile')

    actual_sem = Semester.objects.get(pk=semesterid).semester_of_acad_year
    actual_year = Semester.objects.get(pk=semesterid).actual_year
    sscdata = StudentSemesterCourses.objects.filter(semester=actual_sem)
    course = Course.objects.get(pk=course_id)
    course_name = course.name + ' (' + course.number + ')'
    semesterdict = {1:"Fall", 2:"J-term", 3:"Spring", 4:"Summer"}
    semester_name = semesterdict[actual_sem] + ' of ' + str(actual_year)
    studentlist=[]
    for ssc in sscdata:
        if ssc.actual_year == actual_year:
            for courseinssc in ssc.courses.all():
                if courseinssc.id == int(course_id):
                    studentlist.append(ssc.student.name)
    temp = request.META.items()
    context={'coursename':course_name,'semestername':semester_name,'studentlist':studentlist}
    return render(request, 'student_enrollment_results.html', context)
