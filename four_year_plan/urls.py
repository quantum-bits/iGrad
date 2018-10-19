from django.urls import include, re_path, path

from planner.views import profile

from django.contrib import admin

admin.autodiscover()

urlpatterns = [
    re_path(r'^$', profile),
    re_path(r'planner/', include('planner.urls')),

    re_path(r'accounts/', include('django.contrib.auth.urls')),

    re_path(r'admin/doc/', include('django.contrib.admindocs.urls')),
    path(r'admin/', admin.site.urls),
]
