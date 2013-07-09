from django import forms
from django.contrib.auth.models import User
from django.db.models import Q
from models import *


class RegistrationForm(forms.ModelForm):
    username = forms.CharField(label=(u'User Name'))
    email = forms.EmailField(label=(u'Email Address'))
    password = forms.CharField(label=(u'Password'),
                               widget=forms.PasswordInput(render_value=False))
    
    password1 = forms.CharField(label=(u'Verify Password'),
                                widget=forms.PasswordInput(render_value=False))

    class Meta:
        model = Student
        exclude = ('user',)

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError("That username is already taken; please select another.")

    def clean(self):
        password = self.cleaned_data.get('password')
        password1 = self.cleaned_data.get('password1')
        if password and password1 and password != password1:
            raise forms.ValidationError("The passwords did not match.  Please try again.")

        # something seems to be wrong here -- it doesn't associate the error with
        # password; it does throw the exception, I think (i.e., it returns an error), but
        # it doesn't specifically give the password error message....
        return self.cleaned_data

"""
class AddStudentSemesterForm(forms.ModelForm):
    class Meta:
        model = StudentSemesterCourses
        exclude = ('semester','year','student')

    def __init__(self, *args, **kwargs):
        actyear = kwargs.pop('actual_year')
        sem = kwargs.pop('semester')
        super (AddStudentSemesterForm,self).__init__(*args,**kwargs)
        if sem == 0:
            self.fields['courses'].queryset = Course.objects.all()
        else:
            self.fields['courses'].queryset = Course.objects.filter(Q(semester__actual_year=actyear) 
                                                                    & Q(semester__semester_of_acad_year = sem))

    def clean_student(self):
        courses = self.cleaned_data['courses']
        return courses
"""

class AddCourseForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['planned_courses']

    def __init__(self, *args, **kwargs):
        semester = kwargs.pop('semester')
        super(AddCourseOfferingsForm,self).__init__(*args, **kwargs)
        self.fields['planned_courses'].queryset = CourseOffering.objects.filter(semester=semester)

class AddAdvisingNoteForm(forms.ModelForm):

    class Meta:
        model = AdvisingNote
        exclude = ('student', 'datestamp')

class AddTransferCourse(forms.ModelForm):

    class Meta:
        model = CourseSubstitution
        exclude = ('semester', 'student',)

"""
class AddAdviseeForm(forms.ModelForm):

    class Meta:
        model = Professor
        exclude = ('user', 'name')
"""

class UpdateMajorForm(forms.ModelForm):

    class Meta:
        model = Student
        exclude = ('user', 'university', 'student_id', 'entering_year', 
                   'catalog_year', 'minors', 'first_name', 'last_name',)



