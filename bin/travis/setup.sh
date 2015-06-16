#!/bin/bash
# pwd is the git repo.
set -e

echo "Making settings/local.py"
cat > peekaboo/settings/local.py <<SETTINGS
from . import base
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'peekaboo',
        'USER': 'travis',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '',
    },
}
HMAC_KEYS = {'some': 'thing'}
SECRET_KEY = 'something'
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake'
    }
}

PASSWORD_HASHERS = ['django.contrib.auth.hashers.UnsaltedMD5PasswordHasher']

SETTINGS
