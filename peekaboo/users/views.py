import functools

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib import messages

from peekaboo.main.utils import json_view


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


@superuser_required
def home(request):
    context = {}
    if request.method == 'POST':
        if request.POST.get('staff'):
            user = User.objects.get(pk=request.POST.get('staff'))
            user.is_staff = not user.is_staff
            user.save()
        if request.POST.get('superuser'):
            user = User.objects.get(pk=request.POST.get('superuser'))
            user.is_superuser = not user.is_superuser
            user.save()
        return redirect('users:home')

    users = User.objects.all().order_by('-last_login')
    context['users'] = users
    return render(request, 'users/home.html', context)
