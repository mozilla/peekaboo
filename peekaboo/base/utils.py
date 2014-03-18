"""Utility functions shared by "all" apps"""

import functools

from django import http
from django.conf import settings
from django.shortcuts import redirect
from django.contrib import messages


def ajax_login_required(view_func):
    @functools.wraps(view_func)
    def inner(request, *args, **kwargs):
        if not request.user.is_authenticated():
            return http.HttpResponse('Forbidden', status=403)
        return view_func(request, *args, **kwargs)
    return inner


def superuser_required(view_func):
    @functools.wraps(view_func)
    def inner(request, *args, **kwargs):
        if not request.user.is_authenticated():
            return redirect(settings.LOGIN_URL)
        elif not request.user.is_superuser:
            messages.error(
                request,
                'You need to be a superuser to access this.'
            )
            return redirect(settings.LOGIN_URL)
        return view_func(request, *args, **kwargs)
    return inner
