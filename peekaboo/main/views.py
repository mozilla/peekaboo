import datetime
import time
from collections import defaultdict
from django.shortcuts import render
from django.views.decorators.http import require_POST
from django import http
from .forms import SignInForm
from .models import Visitor
from .utils import json_view


def home(request):
    data = {}
    return render(request, 'main/home.html', data)


def tablet(request):
    data = {}
    data['form'] = SignInForm()
    return render(request, 'main/tablet.html', data)


@require_POST
@json_view
def tablet_signin(request):
    form = SignInForm(request.POST)
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


def log(request):
    data = {}
    return render(request, 'main/log.html', data)


@json_view
def log_entries(request):
    data = {
        'latest': None,
        'rows': []
    }

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
        qs = qs.filter(modified__gte=latest)
    first = None
    for visitor in qs.order_by('modified'):

        row = {
            'id': visitor.pk,
            'modified': format_date(visitor.modified),
            'modified_iso': visitor.modified.isoformat(),
            #'timestamp': time.mktime(visitor.modified.timetuple()),
            'name': visitor.get_name(),
            'thumbnail_url': None,
            'visiting': visitor.visiting,
            'company': visitor.company,
            'email': visitor.email,
        }
        data['rows'].append(row)
        first = visitor.modified
    if first:
        data['latest'] = time.mktime(first.timetuple())
    return data
