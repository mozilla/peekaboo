# This is your project's main settings file that can be committed to your
# repo. If you need to override a setting locally, use settings_local.py

from funfactory.settings_base import *  # NOQA

# Name of the top-level module where you put all your apps.
# If you did not install Playdoh with the funfactory installer script
# you may need to edit this value. See the docs about installing from a
# clone.
PROJECT_MODULE = 'peekaboo'

USE_TZ = True
TIME_ZONE = 'US/Pacific'

# Defines the views served for root URLs.
ROOT_URLCONF = '%s.urls' % PROJECT_MODULE

INSTALLED_APPS = (
    'funfactory',
    'compressor',
    'django_browserid',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'commonware.response.cookies',
    'session_csrf',

    # Application base, containing global templates.
    '%s.base' % PROJECT_MODULE,
    '%s.main' % PROJECT_MODULE,
    '%s.sheet' % PROJECT_MODULE,
    '%s.auth' % PROJECT_MODULE,
    '%s.users' % PROJECT_MODULE,
    '%s.locations' % PROJECT_MODULE,
    'sorl.thumbnail',
    'south',
    'bootstrapform',
    'django.contrib.admin',
    'raven.contrib.django.raven_compat',
    'django_nose',  # deliberately making this the last one
)


LOCALE_PATHS = (
    os.path.join(ROOT, PROJECT_MODULE, 'locale'),
)

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

# Because Jinja2 is the default template loader, add any non-Jinja templated
# apps here:
JINGO_EXCLUDE_APPS = [
    'admin',
    'bootstrapform',
    'browserid',
]

# BrowserID configuration
AUTHENTICATION_BACKENDS = [
    'django_browserid.auth.BrowserIDBackend',
    'django.contrib.auth.backends.ModelBackend',
]

SITE_URL = 'http://localhost:8000'
LOGIN_URL = '/auth/login/'
LOGIN_REDIRECT_URL = '/'
LOGIN_REDIRECT_URL_FAILURE = '/auth/login/'

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'session_csrf.context_processor',
    'django.contrib.messages.context_processors.messages',
    'funfactory.context_processors.globals',
    'peekaboo.main.context_processors.main',
)

# Should robots.txt deny everything or disallow a calculated list of URLs we
# don't want to be crawled?  Default is false, disallow everything.
# Also see http://www.google.com/support/webmasters/bin/answer.py?answer=93710
ENGAGE_ROBOTS = False

# Always generate a CSRF token for anonymous users.
ANON_ALWAYS = True

MIDDLEWARE_CLASSES = (
    'funfactory.middleware.LocaleURLMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'session_csrf.CsrfMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'commonware.middleware.FrameOptionsHeader',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware'
)

# We're never storing any passwords so this can be anything
HMAC_KEYS = {'something': 'anything'}
PASSWORD_HASHERS = ('django.contrib.auth.hashers.MD5PasswordHasher',)

LOGGING = dict(loggers=dict(playdoh={'level': logging.DEBUG}))

SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

# Whether the picture taking part of sign in process should be enabled
DEFAULT_TAKE_PICTURE = True

BROWSERID_REQUEST_ARGS = {'siteName': 'Peek-a-boo!'}

RECYCLE_MINIMUM_HOURS = 30  # days

# Set to True if you want to keep the components that are made to generate
# PDFs when printing badges
DEBUG_PDF_PROGRAM = False

# Default in Django is 2 weeks (1209600 = 60 * 60 * 24 * 7 * 2)
SESSION_COOKIE_AGE = 60 * 60 * 24 * 365  # 1 year
