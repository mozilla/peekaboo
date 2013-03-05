import datetime
import time
from cStringIO import StringIO
from collections import defaultdict
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.files import File
from django import http
from sorl.thumbnail import get_thumbnail
from . import forms
from .models import Visitor
from .utils import json_view


def home(request):
    data = {}
    return render(request, 'main/home.html', data)


def tablet(request):
    data = {}
    data['form'] = forms.SignInForm()
    return render(request, 'main/tablet.html', data)


@require_POST
@json_view
def tablet_signin(request):
    form = forms.SignInForm(request.POST)
    if form.is_valid():
        visitor = form.save()
        data = {
            'id': visitor.pk,
            'name': visitor.get_name(),
        }
        return data
    else:
        errors = defaultdict(list)
        for name, error in form.errors.items():
            errors[name] = error
        return {'errors': errors}

@require_POST
@json_view
@csrf_exempt
def tablet_upload(request, pk):
    visitor = get_object_or_404(Visitor, pk=pk)
    form = forms.PictureForm(request.POST, request.FILES, instance=visitor)
    if form.is_valid():
        form.save()
    # XXX return a nice thumbnail url
    return {'ok': True}


def log(request):
    data = {
        'edit_form': forms.SignInForm(),
    }
    return render(request, 'main/log.html', data)


@json_view
def log_entries(request):
    data = {
        'latest': None,
        'rows': []
    }
    thumbnail_geometry = request.GET.get('thumbnail_geometry', '100')

    def format_date(dt):
        dt_date = dt.strftime('%m/%d/%Y')
        dt_time = dt.strftime('%H:%M')
        dt_tz = dt.tzname() or 'UTC'
        return ' '.join([dt_date, dt_time, dt_tz])

    qs = Visitor.objects.all()
    if request.GET.get('latest'):
        latest = datetime.datetime.fromtimestamp(
            float(request.GET['latest'])
        )
        # because latest is potentially lacking in microseconds
        # add some to prevent fetching it again
        latest += datetime.timedelta(seconds=1)
        qs = qs.filter(created__gte=latest)
    first = None
    for visitor in qs.order_by('created'):

        row = {
            'id': visitor.pk,
            'created': format_date(visitor.created),
            'created_iso': visitor.created.isoformat(),
            'title': visitor.title,
            'name': visitor.get_name(formal=True),
            'thumbnail': None,
            'visiting': visitor.visiting,
            'company': visitor.company,
            'email': visitor.email,
        }
        if visitor.picture:
            thumbnail = get_thumbnail(
                visitor.picture,
                thumbnail_geometry
            )
            row['thumbnail'] = {
                'url': thumbnail.url,
                'width': thumbnail.width,
                'height': thumbnail.height,
            }
        data['rows'].append(row)
        first = visitor.created
    if first:
        data['latest'] = time.mktime(first.timetuple())
    return data


@json_view
def log_entry(request, pk):
    visitor = get_object_or_404(Visitor, pk=pk)
    thumbnail_geometry = request.GET.get('thumbnail_geometry', '100')

    if request.method == 'POST':
        form = forms.SignInForm(request.POST, instance=visitor)
        if form.is_valid():
            form.save()
            data = form.cleaned_data
        else:
            raise NotImplementedError
    else:
        data = {
            'first_name': visitor.first_name,
            'last_name': visitor.last_name,
            'title': visitor.title,
            'email': visitor.email,
            'company': visitor.company,
            'visiting': visitor.visiting,
            'thumbnail_url': None,
        }
    if visitor.picture:
        thumbnail = get_thumbnail(
            visitor.picture,
            thumbnail_geometry
        )
        data['thumbnail'] = {
            'url': thumbnail.url,
            'width': thumbnail.width,
            'height': thumbnail.height,
        }
    return data
