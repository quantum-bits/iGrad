from django.conf.urls import patterns, include, url

urlpatterns = patterns(
    'planner.views',

    url(r'^home/$', 'home'),

    url(r'^register/$', 'student_registration', name='register'),
    url(r'^profile/$', 'profile', name='profile'),

    url(r'^changemajor/$', 'update_major', name='update_major'),
    url(r'^updatesemester/(\d+)/$', 'update_student_semester', name='update_student_semester'),
    url(r'^fouryearplan/$', 'display_four_year_plan', name='four_year_plan'),
    url(r'^graduationaudit/$', 'display_grad_audit', name='grad_audit'),

    url(r'^advisingnotes/', 'display_advising_notes', name='advising_notes'),
    url(r'^addadvisingnote/', 'add_new_advising_note', name='add_new_note'),
    url(r'^updateNote/(\d+)/$', 'update_advising_note', name='update_note'),
    url(r'^deleteNote/(\d+)/$', 'delete_advising_note', name='delete_note'),

    url(r'^add_course_substitute/(\d+)/$', 'add_course_substitute', name='add_sub'),
    url(r'^delete_course_sub/(\d+)/$', 'delete_course_substitution', name='delete_course_sub'),
    url(r'^updatecyoc/(\d+)/(\d+)/$', 'update_create_your_own_course', name='update_cyoc'),

    url(r'^remove_course_from_plan/(\d+)/$', 'remove_course_from_plan', name='remove_course_from_plan'),
    url(r'^move_course_to_new_semester/(\d+)/(\d+)/$', 'move_course_to_new_semester', name='move_course'),

    url(r'^changeadvisee/(\d+)/$', 'update_advisee', name='update_advisee'),
    url(r'^search/$', 'search', name='search'),
    url(r'^viewstudents/(\d+)/(\d+)/$', 'view_enrolled_students', name='view_students'),


)
