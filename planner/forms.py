from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm
from four_year_plan_v1.majors.models import Student, StudentSemesterCourses, Course, CreateYourOwnCourse, AdvisingNote, Professor
from django.db.models import Q

class RegistrationForm(ModelForm):
    username = forms.CharField(label=(u'User Name'))
    email = forms.EmailField(label=(u'Email Address'))
    password = forms.CharField(label=(u'Password'), widget=forms.PasswordInput(render_value=False))
    password1 = forms.CharField(label=(u'Verify Password'), widget=forms.PasswordInput(render_value=False))

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
# something seems to be wrong here -- it doesn't associate the error with password; it does
# throw the exception, I think (i.e., it returns an error), but it doesn't specifically give the password
# error message....
        return self.cleaned_data

class LoginForm(forms.Form):
    username = forms.CharField(label=(u'User Name'))
    password = forms.CharField(label=(u'Password'), widget=forms.PasswordInput(render_value=False))

# the following is no longer used, but maybe a good idea to keep it for a bit, just in case.
#class SaveStudentSemesterForm(ModelForm):
#
#    class Meta:
#        model = StudentSemesterCourses
#        exclude = ('semester','year','student')

class AddStudentSemesterForm(ModelForm):

    class Meta:
        model = StudentSemesterCourses
        exclude = ('semester','year','student')

    def __init__(self,*args,**kwargs):
#        assert False, locals()
        actyear=kwargs.pop('actualyear')
        sem=kwargs.pop('semester')
        super (AddStudentSemesterForm,self).__init__(*args,**kwargs)
#        kwargs=args[0]
#        assert False, locals()
        if sem == 0:
            self.fields['courses'].queryset = Course.objects.all()
        else:
            self.fields['courses'].queryset = Course.objects.filter(Q(semester__actual_year=actyear) 
                    & Q(semester__semester_of_acad_year = sem))

    def clean_student(self):
        courses = self.cleaned_data['courses']
        return courses

class AddAdvisingNoteForm(ModelForm):

    class Meta:
        model = AdvisingNote
        exclude = ('student','datestamp')

class AddCreateYourOwnCourseForm(ModelForm):

    class Meta:
        model = CreateYourOwnCourse
        exclude = ('semester','actual_year','student')

class AddAdviseeForm(ModelForm):

    class Meta:
        model = Professor
        exclude = ('user','name')

class UpdateMajorForm(ModelForm):

    class Meta:
        model = Student
        exclude = ('user','name','entering_year',)
