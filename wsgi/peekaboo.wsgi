import os
import site

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peekaboo.settings')

# Add the app dir to the python path so we can import manage.
wsgidir = os.path.dirname(__file__)
site.addsitedir(os.path.abspath(os.path.join(wsgidir, '../')))


from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
