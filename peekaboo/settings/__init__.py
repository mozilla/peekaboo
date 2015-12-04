import sys
import os
from .base import *  # NOQA


try:
    from .local import *  # NOQA
except ImportError, exc:
    exc.args = tuple(
        ['%s (did you rename settings/local.py-dist?)' % exc.args[0]]
    )
    raise exc


if len(sys.argv) > 1 and sys.argv[1] == 'test':
    from .test import *  # NOQA

    # Are you getting full benefit from django-nose?
    if not os.getenv('REUSE_DB', 'false').lower() in ('true', '1', ''):
        print (
            "Note!\n\tIf you want much faster tests in local development "
            "consider setting the REUSE_DB=1 environment variable.\n"
        )
