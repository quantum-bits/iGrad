from django.conf.urls import patterns, include, url

urlpatterns = patterns(
    'planner.views',

    url(r'^home/$', 'home'),

    url(r'^register/$', 'student_registration'),
    url(r'^profile/$', 'profile', name='profile'),

    url(r'^changemajor/(\d+)/$', 'update_major'),
    url(r'^updatesemester/(\d+)/$', 'update_student_semester', name='update_student_semester'),
    url(r'^fouryearplan/$', 'display_four_year_plan', name='four_year_plan'),
    url(r'^graduationaudit/$', 'display_grad_audit', name='grad_audit'),

    url(r'^advisingnotes/', 'display_advising_notes', name='advising_notes'),
    url(r'^addadvisingnote/', 'add_new_advising_note', name='add_new_note'),
    url(r'^updateNote/(\d+)/$', 'update_advising_note', name='update_note'),
    url(r'^deleteNote/(\d+)/$', 'delete_advising_note', name='delete_note'),

    url(r'^addcreateyourowncourse/(\d+)/$', 'add_create_your_own_course'),
    url(r'^deletecyoc/(\d+)/(\d+)/(\d+)/$', 'delete_create_your_own_course', name='delete_cyoc'),
    url(r'^updatecyoc/(\d+)/(\d+)/$', 'update_create_your_own_course'),

    url(r'^deletecourse/(\d+)/(\d+)/(\d+)/$', 'delete_course_inside_SSCObject', name='delete_course'),
    url(r'^movecoursetonewsemester/(\d+)/(-?\d+)/(\d+)/(\d+)/$', 'move_course_to_new_SSCObject', name='move_course'),

    url(r'^changeadvisee/(\d+)/$', 'update_advisee', name='update_advisee'),
    url(r'^search/$', 'search'),
    url(r'^viewstudents/(\d+)/(\d+)/$', 'view_enrolled_students'),


)
