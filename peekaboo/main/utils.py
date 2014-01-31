import json
import functools

from django.shortcuts import redirect
from django import http
from django.contrib import messages
from django.conf import settings


def json_view(f):
    @functools.wraps(f)
    def wrapper(*args, **kw):
        response = f(*args, **kw)
        if isinstance(response, http.HttpResponse):
            return response
        else:
            return http.HttpResponse(
                _json_clean(json.dumps(response)),
                content_type='application/json; charset=UTF-8'
            )
    return wrapper


def _json_clean(value):
    """JSON-encodes the given Python object."""
    # JSON permits but does not require forward slashes to be escaped.
    # This is useful when json data is emitted in a <script> tag
    # in HTML, as it prevents </script> tags from prematurely terminating
    # the javscript. Some json libraries do this escaping by default,
    # although python's standard library does not, so we do it here.
    # http://stackoverflow.com/questions/1580647/json-why-are-forward\
    # -slashes-escaped
    return value.replace("</", "<\\/")


def non_mortals_required(view_func):
    @functools.wraps(view_func)
    def inner(request, *args, **kwargs):
        if not request.user.is_authenticated():
            return redirect(settings.LOGIN_URL)
        elif not (request.user.is_staff or request.user.is_superuser):
            messages.error(
                request,
                'You need special permission to reach this.'
            )
            return redirect('/')
        return view_func(request, *args, **kwargs)
    return inner
