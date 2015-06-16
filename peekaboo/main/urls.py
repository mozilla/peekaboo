from django.conf.urls.defaults import patterns, url, include

from . import views


urlpatterns = patterns(
    '',
    url('^robots\.txt$',
        views.robots_txt,
        name='robots_txt'),
    url(r'^$', views.home,
        name='home'),
    url(r'^log/$', views.log_start,
        name='log_start'),
    url(r'^log/(?P<location>[\w-]+)/$', views.log,
        name='log'),
    url(r'^log/(?P<location>[\w-]+)/entries/$', views.log_entries,
        name='log_entries'),
    url(r'^log/entry/(?P<pk>\d+)/$', views.log_entry,
        name='log_entry'),
    url(r'^log/entry/(?P<pk>\d+)/picture\.jpg$', views.log_entry_picture,
        {'format': 'jpg'}, name='log_entry_picture'),
    url(r'^log/entry/(?P<pk>\d+)/delete/$', views.delete_entry,
        name='delete_entry'),
    url(r'^log/entry/(?P<pk>\d+)/print/$', views.print_entry,
        name='print_entry'),
    url(r'^log/entry/(?P<pk>\d+)/print.pdf$', views.print_entry_pdf,
        name='print_entry_pdf'),
    url(r'^stats/$', views.stats_start,
        name='stats_start'),
    url(r'^stats/(?P<location>[\w-]+)/$', views.stats,
        name='stats'),
    url(r'^browserid/', include('django_browserid.urls')),
    url(r'^logout/?$', 'django.contrib.auth.views.logout', {'next_page': '/'},
        name='logout'),
    url(r'^debugger', views.debugger),
    url(r'^csv/$', views.csv_upload,
        name='csv_upload'),
)
