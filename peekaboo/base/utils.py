"""Utility functions shared by "all" apps"""

import functools
from django import http


def ajax_login_required(view_func):
    @functools.wraps(view_func)
    def inner(request, *args, **kwargs):
        if not request.user.is_authenticated():
            return http.HttpResponse('Forbidden', status=403)
        return view_func(request, *args, **kwargs)
    return inner
