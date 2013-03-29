from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'four_year_plan.views.home', name='home'),
    # url(r'^four_year_plan/', include('four_year_plan.foo.urls')),

    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)


#     url(r'home/$', 'studentform.views.Home'),
#     url(r'register/$', 'studentform.views.StudentRegistration'),
#     url(r'login/$', 'studentform.views.LoginRequest'),
#     url(r'logout/$', 'studentform.views.LogoutRequest'),
#     url(r'profile/$', 'studentform.views.Profile'),
#     url(r'changemajor/(\d+)/$', 'studentform.views.UpdateMajor'),
#     url(r'updatesemester/(\d+)/$', 'studentform.views.UpdateStudentSemester'),
#     url(r'fouryearplan/$', 'studentform.views.DisplayFourYearPlan'),
#     url(r'graduationaudit/$', 'studentform.views.DisplayGradAudit'),
#     url(r'advisingnotes/', 'studentform.views.DisplayAdvisingNotes'),
#     url(r'addadvisingnote/', 'studentform.views.AddNewAdvisingNote'),
#     url(r'updateNote/(\d+)/$', 'studentform.views.UpdateAdvisingNote'),
#     url(r'deleteNote/(\d+)/$', 'studentform.views.DeleteAdvisingNote'),
#     url(r'addcreateyourowncourse/(\d+)/$', 'studentform.views.AddCreateYourOwnCourse'),
#     url(r'deletecyoc/(\d+)/(\d+)/(\d+)/$', 'studentform.views.DeleteCreateYourOwnCourse'),
#     url(r'updatecyoc/(\d+)/(\d+)/$', 'studentform.views.UpdateCreateYourOwnCourse'),
#     url(r'deletecourse/(\d+)/(\d+)/(\d+)/$', 'studentform.views.DeleteCourseInsideSSCObject'),
#     url(r'movecoursetonewsemester/(\d+)/(-?\d+)/(\d+)/(\d+)/$', 'studentform.views.MoveCourseToNewSSCObject'),
#     url(r'changeadvisee/(\d+)/$', 'studentform.views.UpdateAdvisee'),
#     url(r'search/$', 'studentform.views.search'),
#     url(r'viewstudents/(\d+)/(\d+)/$', 'studentform.views.ViewEnrolledStudents'),
