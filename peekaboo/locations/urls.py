from django.conf.urls import patterns, url

from . import views


urlpatterns = patterns(
    '',
    url(r'^$', views.home, name='home'),
    url(r'^(?P<pk>\d+)/edit/$', views.edit, name='edit'),
    url(r'^new/$', views.new, name='new'),
)
