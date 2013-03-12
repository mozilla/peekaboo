from .base import *
try:
    from .local import *
except ImportError, exc:
    try:
        from .stackato import *
    except ImportError:
        exc.args = tuple(['%s (did you rename settings/local.py-dist?)' % exc.args[0]])
        raise exc
