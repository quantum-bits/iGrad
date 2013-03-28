from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'four_year_plan.views.home', name='home'),
    # url(r'^four_year_plan/', include('four_year_plan.foo.urls')),

    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)


# urlpatterns = patterns(
#     '',
#     # Examples:
#     # url(r'^$', 'four_year_plan_v1.views.home', name='home'),
#     # url(r'^four_year_plan_v1/', include('four_year_plan_v1.foo.urls')),

#     # Uncomment the admin/doc line below to enable admin documentation:
#     # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

#     # Uncomment the next line to enable the admin:
#     url(r'^admin/', include(admin.site.urls)),
#     #    url(r'^contact/$', 'contact.views.contact'),
#     #    url(r'^student/$', 'studentform.views.student'),
#     url(r'home/$', 'studentform.views.Home'),
#     url(r'register/$', 'studentform.views.StudentRegistration'),
#     url(r'login/$', 'studentform.views.LoginRequest'),
#     url(r'logout/$', 'studentform.views.LogoutRequest'),
#     url(r'^resetpassword/passwordsent/$', 'django.contrib.auth.views.password_reset_done'),
#     url(r'^resetpassword/$', 'django.contrib.auth.views.password_reset'),
#     url(r'^reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', 'django.contrib.auth.views.password_reset_confirm'),
#     url(r'^reset/done/$', 'django.contrib.auth.views.password_reset_complete'),
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
# )
