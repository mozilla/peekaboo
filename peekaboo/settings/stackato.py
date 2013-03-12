import os
try:
    import dj_database_url
except ImportError:
    dj_database_url = None

if dj_database_url and os.environ.get('DATABASE_URL'):
    DATABASES = {
        'default': dj_database_url.config()
        # 'slave': {
        # ...
        # },
    }
    if 'mysql' in DATABASES['default']['ENGINE']:
        opt = DATABASES['default'].get('OPTIONS', {})
        opt['init_command'] = 'SET storage_engine=InnoDB'
        opt['charset'] = 'utf8'
        opt['use_unicode'] = True
        DATABASES['default']['OPTIONS'] = opt
    DATABASES['default']['TEST_CHARSET'] = 'utf8'
    DATABASES['default']['TEST_COLLATION'] = 'utf8_general_ci'


if os.environ.get('MEMCACHE_URL'):
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
            'LOCATION': os.environ['MEMCACHE_URL'],
            'TIMEOUT': 500
        }
    }


import json
VCAP_APP = json.loads(os.environ['VCAP_APPLICATION'])

# True if we running as a Stackato instance.
assert VCAP_APP, "No VCAP_APPLICATION"

# TODO(Kumar): check for https?
SITE_URL = ('http://%s' % VCAP_APP['uris'][0] if VCAP_APP
            else 'http://127.0.0.1:8000')


if os.environ.get('DJANGO_SECRET_KEY'):
    SECRET_KEY = os.environ['DJANGO_SECRET_KEY']
else:
    # This must be set in settings/local.py
    SECRET_KEY = ''

if os.environ.get('DJANGO_HMAC_KEY'):
    HMAC_KEYS = {
        'stackato': os.environ['DJANGO_HMAC_KEY']
    }
    from django_sha2 import get_password_hashers
    PASSWORD_HASHERS = get_password_hashers(BASE_PASSWORD_HASHERS, HMAC_KEYS)


# Currently, Mozilla's Stackato only has a self-signed https cert.
# TODO: fix this when we have https support.
SESSION_COOKIE_SECURE = False
# TODO: remove this when we have a way to see exceptions on Stackato.
DEBUG = TEMPLATE_DEBUG = True

MEDIA_ROOT = os.environ['STACKATO_FILESYSTEM_MEDIA']
