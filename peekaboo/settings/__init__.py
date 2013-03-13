import os
from .base import *

if os.environ.get('VCAP_APPLICATION'):
    # we're in Stackto land!
    from .stackato import *
else:
    try:
        from .local import *
    except ImportError, exc:
        exc.args = tuple(['%s (did you rename settings/local.py-dist?)' % exc.args[0]])
        raise exc
