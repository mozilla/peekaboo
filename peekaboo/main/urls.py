from django.conf.urls.defaults import *

from . import views


urlpatterns = patterns('',
    url(r'^$', views.home, name='main.home'),
    url(r'^tablet/$', views.tablet, name='main.tablet'),
    url(r'^tablet/upload/(?P<pk>\d+)/$', views.tablet_upload,
        name='main.tablet_upload'),
    url(r'^tablet/signin/$', views.tablet_signin,
        name='main.tablet-sign-in'),
    url(r'^log/$', views.log, name='main.log'),
    url(r'^log/entries/$', views.log_entries, name='main.log_entries'),
    url(r'^log/(?P<pk>\d+)/$', views.log_entry, name='main.log_entry'),
    url(r'^browserid/', include('django_browserid.urls')),
    url(r'^logout/?$', 'django.contrib.auth.views.logout', {'next_page': '/'},
        name='main.logout'),
)
