from django.urls import re_path, path, include

from . import views
#from planner.views import profile

urlpatterns = [

    path(r'home/', views.home),
    path(r'register/', views.student_registration, name='planner.views.register'),
    path(r'profile/', views.profile, name='planner.views.profile'),

    re_path(r'^changemajor/(\d+)/$', views.update_major, name='planner.views.update_major'),
    re_path(r'^updatesemester/(\d+)/$', views.update_student_semester, name='planner.views.update_student_semester'),
    re_path(r'^fouryearplan/$', views.display_four_year_plan, name='planner.views.display_four_year_plan'),
    re_path(r'^graduationaudit/$', views.display_grad_audit, name='planner.views.display_grad_audit'),

    re_path(r'^advisingnotes/', views.display_advising_notes, name='planner.views.display_advising_notes'),
    re_path(r'^addadvisingnote/', views.add_new_advising_note, name='planner.views.add_new_note'),
    re_path(r'^updateNote/(\d+)/$', views.update_advising_note, name='planner.views.update_note'),
    re_path(r'^deleteNote/(\d+)/$', views.delete_advising_note, name='planner.views.delete_note'),

    re_path(r'^addcreateyourowncourse/(\d+)/$', views.add_create_your_own_course, name='planner.views.add_cyoc'),
    re_path(r'^deletecyoc/(\d+)/(\d+)/(\d+)/$', views.delete_create_your_own_course, name='planner.views.delete_cyoc'),
    re_path(r'^updatecyoc/(\d+)/(\d+)/$', views.update_create_your_own_course, name='planner.views.update_cyoc'),

    re_path(r'^deletecourse/(\d+)/(\d+)/(\d+)/$', views.delete_course_inside_SSCObject, name='planner.views.delete_course'),
    re_path(r'^movecoursetonewsemester/(\d+)/(-?\d+)/(\d+)/(\d+)/$', views.move_course_to_new_SSCObject, name='planner.views.move_course'),

    re_path(r'^changeadvisee/(\d+)/$', views.update_advisee, name='planner.views.update_advisee'),
    re_path(r'^search/$', views.search, name='planner.views.search'),
    re_path(r'^viewstudents/(\d+)/(\d+)/$', views.view_enrolled_students, name='planner.views.view_students'),


]
