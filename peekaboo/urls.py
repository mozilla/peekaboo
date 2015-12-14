from django.conf import settings
from django.conf.urls import patterns, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from peekaboo.base.monkeypatches import patch


patch()

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    (r'^(?P<path>contribute\.json)$', 'django.views.static.serve',
     {'document_root': settings.ROOT}),
    (r'', include('peekaboo.main.urls', namespace='main')),
    (r'^sheet/', include('peekaboo.sheet.urls', namespace='sheet')),
    (r'^auth/', include('peekaboo.authentication.urls', namespace='auth')),
    (r'^users/', include('peekaboo.users.urls', namespace='users')),
    (r'^locations/',
     include('peekaboo.locations.urls', namespace='locations')),
    (r'^admin/', include(admin.site.urls)),
    (r'^browserid/', include('django_browserid.urls')),
)

# In DEBUG mode, serve media files through Django.
if settings.DEBUG:
    # Remove leading and trailing slashes so the regex matches.
    media_url = settings.MEDIA_URL.lstrip('/').rstrip('/')
    urlpatterns += patterns(
        '',
        (r'^%s/(?P<path>.*)$' % media_url, 'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT}),
    )
    urlpatterns += staticfiles_urlpatterns()
