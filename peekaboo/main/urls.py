from django.conf.urls.defaults import *

from . import views


urlpatterns = patterns('',
    url(r'^$', views.home, name='main.home'),
    url(r'^tablet/$', views.tablet, name='main.tablet'),
    url(r'^tablet/signin/$', views.tablet_signin,
        name='main.tablet-sign-in'),
    url(r'^log/$', views.log, name='main.log'),
    url(r'^log/entries/$', views.log_entries, name='main.log_entries'),
    url(r'^browserid/', include('django_browserid.urls')),
    url(r'^logout/?$', 'django.contrib.auth.views.logout', {'next_page': '/'},
        name='main.logout'),
)
