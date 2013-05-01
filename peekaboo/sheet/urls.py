from django.conf.urls.defaults import patterns, url

from . import views


urlpatterns = patterns('',
    url(r'^$', views.home,
        name='home'),
    url(r'^upload/(?P<pk>\d+)/$', views.upload,
        name='upload'),
    url(r'^signin/$', views.signin,
        name='sign_in'),
    url(r'^locations/$', views.locations,
        name='locations'),
)
