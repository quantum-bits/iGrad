
@login_required
def DisplayGradAudit(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/login/')
    studentlocal = request.user.get_profile

    # check if the "student" is actually a professor....

    temp = Professor.objects.all().filter(user=studentlocal)

    if len(temp) == 0: # this is a student
        isProfessor=False
    else:
        isProfessor=True
        studentlocal = temp[0].advisee
        if studentlocal == None: #no advisee currently selected; go pick one first
            return HttpResponseRedirect('/changeadvisee/2/')

    tempdata = StudentSemesterCourses.objects.all().filter(student=studentlocal)
    tempdata2 = Student.objects.all().filter(user=studentlocal)
    tempdata3 = CreateYourOwnCourse.objects.all().filter(student=studentlocal)

    studentid = tempdata[0].student.id
    prenotmetlist, conotmetlist = PreCoReqCheck(studentid)

    if tempdata2.major == None:
        hasMajor = False
        context = {'student': studentlocal,'isProfessor': isProfessor,'hasMajor':hasMajor}
        return render_to_response('fouryearplan.html', context, context_instance=RequestContext(request))
    else:
        hasMajor = True

    assert False, locals()

    # ssclist is used for later on when we try to find other semesters that a given course is offered
    ssclist=[]
    for ssc in tempdata:
        if ssc.semester !=0:  # don't include pre-TU ssc object here
            numcrhrsthissem = 0
            for course in ssc.courses.all():
                numcrhrsthissem = numcrhrsthissem + course.credit_hours
            # now add in credit hours from any create your own type courses
            tempdata4 = tempdata2.filter(Q(semester=ssc.semester)&Q(actual_year=ssc.actual_year))
            for course in tempdata4:
                numcrhrsthissem = numcrhrsthissem + course.credit_hours
            ssclist.append([ssc.id, ssc.actual_year, ssc.semester, numcrhrsthissem])

    termdictionaryalphabetize={0:"aPre-TU", 1:"eFall", 2:"bJ-term", 3:"cSpring", 4:"dSummer"}
    termdictionary={0:"Pre-TU", 1:"Fall", 2:"J-term", 3:"Spring", 4:"Summer"}
    
# first, form an array containing the info for the "create your own" type courses
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
# "alphabetize" the semesters...
    for sem1 in tempdata:
        semestercontainscyoc = False
        tempcoursename=[]
        semtemp = sem1.semester
        actyeartemp = sem1.actual_year
        totalcredithrs = 0
        tempcyocarray =[]
        ii = 0
        for row in cyocarray:
            if row[0] == actyeartemp and row[1] == termdictionaryalphabetize[semtemp]:
                tempcyocarray.append(ii)
            ii=ii+1
        for indexii in reversed(tempcyocarray):
            temparray = cyocarray.pop(indexii)
            totalcredithrs = totalcredithrs+temparray[4]
            iscyoc = True
            semestercontainscyoc = True
            tempcoursename.append([temparray[2], temparray[3], temparray[4], 
                                   temparray[5], temparray[6], iscyoc, temparray[7],[]])
        for cc in sem1.courses.all():
            iscyoc = False
            totalcredithrs = totalcredithrs + cc.credit_hours
            allsemestersthiscourse = cc.semester.all()
            # form an array of other semesters when this course is offered
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
                    if elementid == -1: # id wasn't found, meaning this course offering is not during a time the student is at TU
                        keepthisone = False
                if keepthisone == True:
                    semarraynonordered.append([yearotheroffering, semotheroffering, elementid, numhrsthissem])

            semarrayreordered=ReorderList(semarraynonordered)
            semarray=[]
            for row in semarrayreordered:
                semarray.append([NamedYear(enteringyear, row[0], row[1]),row[2], row[3]])
    
            tempcoursename.append([cc.name,cc.number,cc.credit_hours,cc.sp,cc.cc,iscyoc, cc.id,semarray])
        datablock.append([actyeartemp, termdictionaryalphabetize[semtemp], sem1.student.name, tempcoursename, sem1.id, totalcredithrs,
                          semestercontainscyoc])
        totalcredithoursfouryears=totalcredithoursfouryears+totalcredithrs

# initial sort
    datablock2 = sorted(datablock, key=lambda rrow: (rrow[0], rrow[1]))
    datablock3 = []
    for row in datablock2:
        row[1]=row[1][1:]
        datablock3.append(row)    

    if totalcredithoursfouryears > 159:
        credithrmaxreached = True
    else:
        credithrmaxreached = False

#    assert False, locals()

# now organize the 21 (pre-TU, plus 4 for each of freshman,..., super-senior) lists into 6 
# (pre-TU, freshman, etc.)

# first check to make sure that there are, in fact, 21 rows....
    if len(datablock3)!=21:
        assert False, locals()

    yearlist=[[0],[1,2,3,4],[5,6,7,8],[9,10,11,12],[13,14,15,16],[17,18,19,20]]
    datablock4=[]
    for year in yearlist:
        temp=[]
        for semester in year:
            temp.append(datablock3[semester])
        datablock4.append(temp)

    context = {'student': studentlocal, 'datablock':datablock4,
               'totalhrsfouryears':totalcredithoursfouryears, 'credithrmaxreached':credithrmaxreached, 
               'isProfessor': isProfessor}
    return render_to_response('fouryearplan.html', context, context_instance=RequestContext(request))
		
