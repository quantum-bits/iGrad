from django.conf.urls import patterns, include, url

urlpatterns = patterns(
    'planner.views',

    url(r'^$', 'home'),
    url(r'^register/$', 'student_registration'),
    url(r'^login/$', 'login_request'),
    url(r'^logout/$', 'logout_request'),
    url(r'^profile/$', 'profile'),
    url(r'^changemajor/(\d+)/$', 'update_major'),
    url(r'^updatesemester/(\d+)/$', 'update_student_semester'),
    url(r'^fouryearplan/$', 'display_four_year_plan'),
    url(r'^graduationaudit/$', 'display_grad_audit'),
    url(r'^advisingnotes/', 'display_advising_notes'),
    url(r'^addadvisingnote/', 'add_new_advising_note'),
    url(r'^updateNote/(\d+)/$', 'update_advising_note'),
    url(r'^deleteNote/(\d+)/$', 'delete_advising_note'),
    url(r'^addcreateyourowncourse/(\d+)/$', 'add_create_your_own_course'),
    url(r'^deletecyoc/(\d+)/(\d+)/(\d+)/$', 'delete_create_your_own_course'),
    url(r'^updatecyoc/(\d+)/(\d+)/$', 'update_create_your_own_course'),
    url(r'^deletecourse/(\d+)/(\d+)/(\d+)/$', 'delete_course_inside_SSCObject'),
    url(r'^movecoursetonewsemester/(\d+)/(-?\d+)/(\d+)/(\d+)/$', 'move_course_to_new_SSCObject'),
    url(r'^changeadvisee/(\d+)/$', 'update_advisee'),
    url(r'^search/$', 'search'),
    url(r'^viewstudents/(\d+)/(\d+)/$', 'view_enrolled_students'),
)
