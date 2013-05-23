from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from django_browserid.auth import BrowserIDBackend


class SelectiveBrowserIDBackend(BrowserIDBackend):

    def is_valid_email(self, email):
        allowed = getattr(settings, 'ALLOWED_EMAIL_ADDRESSES', None)
        if not allowed:
            raise ImproperlyConfigured(
                'settings.ALLOWED_EMAIL_ADDRESSES not set up or empty. '
                'See settings/local.py-dist'
            )
        return email in allowed
