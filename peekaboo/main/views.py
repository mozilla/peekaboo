import calendar
import functools
import os
import subprocess
import tempfile
import shutil
import stat
import time
import datetime
import time
from cStringIO import StringIO
from collections import defaultdict
from pyquery import PyQuery as pq
from django import http
from django.utils.timezone import utc, make_aware
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.files import File
from sorl.thumbnail import get_thumbnail
from . import forms
from .models import Visitor, Location
from .utils import json_view


def ajax_login_required(view_func):
    @functools.wraps(view_func)
    def inner(request, *args, **kwargs):
        if not request.user.is_authenticated():
            return http.HttpResponse('Forbidden', status=403)
        return view_func(request, *args, **kwargs)
    return inner


def robots_txt(request):
    return http.HttpResponse(
        'User-agent: *\n'
        '%s: /' % ('Allow' if settings.ENGAGE_ROBOTS else 'Disallow'),
        mimetype='text/plain',
    )


@login_required
def home(request):
    data = {}
    return render(request, 'main/home.html', data)


@login_required
def log_start(request):
    data = {}
    return render(request, 'main/log-start.html', data)


@login_required
def log(request, location):
    location = get_object_or_404(Location, slug=location)
    data = {
        'edit_form': forms.SignInForm(),
        'location': location,
    }
    request.session['default-location'] = location.slug
    return render(request, 'main/log.html', data)


@json_view
@ajax_login_required
def log_entries(request, location):
    data = {
        'latest': None,
        'created': [],
        'modified': []
    }
    location = get_object_or_404(Location, slug=location)
    thumbnail_geometry = request.GET.get('thumbnail_geometry', '100')

    def format_date(dt):
        dt_date = dt.strftime('%m/%d/%Y')
        dt_time = dt.strftime('%H:%M')
        dt_tz = dt.tzname() or 'UTC'
        return ' '.join([dt_date, dt_time, dt_tz])

    qs = Visitor.objects.filter(location=location)
    if request.GET.get('latest'):
        latest = datetime.datetime.utcfromtimestamp(
            float(request.GET['latest'])
        )
        latest = latest.replace(tzinfo=utc)

        # because latest is potentially lacking in microseconds
        # add some to prevent fetching it again
        latest += datetime.timedelta(seconds=1)
        recently_created = qs.filter(created__gte=latest)
    else:
        latest = None
        recently_created = qs

    def make_row(visitor):
        row = {
            'id': visitor.pk,
            'created': format_date(visitor.created),
            'created_iso': visitor.created.isoformat(),
            'job_title': visitor.job_title,
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
        return row

    first = None
    for visitor in recently_created.order_by('created'):
        row = make_row(visitor)
        data['created'].append(row)
        first = max(visitor.created, visitor.modified)

    # now how about those recently updated
    if latest:
        recently_modified = qs.filter(
            created__lt=latest,
            modified__gt=latest
        )
        for visitor in recently_modified.order_by('modified'):
            row = make_row(visitor)
            assert row not in data['created']
            data['modified'].append(row)
            first = visitor.modified

    if first:
        data['latest'] = calendar.timegm(first.utctimetuple())

    return data


@json_view
@csrf_exempt
def log_entry(request, pk):
    visitor = get_object_or_404(Visitor, pk=pk)
    thumbnail_geometry = request.GET.get('thumbnail_geometry', '100')

    if request.method == 'POST':
        form = forms.SignInEditForm(request.POST, instance=visitor)
        if form.is_valid():
            form.save()
            data = form.cleaned_data
        else:
            return {'errors': form.errors}
    else:
        data = {
            'first_name': visitor.first_name,
            'last_name': visitor.last_name,
            'job_title': visitor.job_title,
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


@login_required
@json_view
@require_POST
def delete_entry(request, pk):
    visitor = get_object_or_404(Visitor, pk=pk)
    visitor.delete()
    # XXX delete all images too??
    return {'deleted': True}


@login_required
def print_entry(request, pk):
    visitor = get_object_or_404(Visitor, pk=pk)
    data = {
        'visitor': visitor,
    }
    return render(request, 'main/print-entry.html', data)


@login_required
def print_entry_pdf(request, pk):
    visitor = get_object_or_404(Visitor, pk=pk)
    data = {
        'visitor': visitor,
    }
    response = render(request, 'main/print-entry.pdf.html', data)
    html = response.content

    tmp_dir = os.path.join(
        tempfile.gettempdir(),
        'peekaboopdfs'
    )
    if not os.path.isdir(tmp_dir):
        os.mkdir(tmp_dir)

    input_file = os.path.join(tmp_dir, 'visitor-%s.html' % visitor.pk)
    output_file = os.path.join(tmp_dir, 'visitor-%s.pdf' % visitor.pk)

    dom = pq(html)

    for img in dom('img'):
        src = img.attrib['src']
        if settings.STATIC_URL in src:
            source = os.path.join(
                settings.STATIC_ROOT,
                src.replace(settings.STATIC_URL, '')
            )
        else:
            source = os.path.join(
                settings.MEDIA_ROOT,
                src.replace(settings.MEDIA_URL, '')
            )
        if not os.path.isfile(source):
            raise IOError("Couldn't find %s (Tried: %s)" %
                (img.attrib['src'], source)
            )
        filename = os.path.basename(source)
        destination = os.path.join(
            tmp_dir, filename
        )
        if os.path.isfile(destination):
            age = time.time() - os.stat(destination)[stat.ST_MTIME]
            if settings.DEBUG or age > 60 * 60:
                shutil.copyfile(source, destination)
        else:
            shutil.copyfile(source, destination)
        html = html.replace(img.attrib['src'], filename)

    with open(input_file, 'w') as f:
        f.write(html)

    pdf_program = getattr(settings, 'PDF_PROGRAM', 'wkhtmltopdf')
    if 'wkpdf' in pdf_program:
        cmd = (
            pdf_program +
            ' --orientation %(orientation)s'
            ' --source %(input_file)s --output %(output_file)s'
        )
    elif 'wkhtmltopdf' in pdf_program:
        cmd = (
            pdf_program +
            ' --orientation %(orientation)s'
            ' %(input_file)s %(output_file)s'
        )
    cmd = cmd % {
        'input_file': input_file,
        'output_file': output_file,
        'orientation': 'landscape',
    }
    proc = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    out, err = proc.communicate()
    exit_code = proc.returncode
    #print output_file
    #print "EXIT"
    #print exit_code
    #print "OUT"
    #print out
    #print "ERR"
    #print err
    #print
    #print "FILE CREATED", os.path.isfile(output_file) and "Yes!" or "No"
    #print '-' * 70
    if os.path.isfile(output_file):
        response['Content-Disposition'] = (
            'filename="%s.pdf"' % os.path.basename(output_file)
        )
        response = http.HttpResponse(mimetype='application/pdf')
        response.write(open(output_file).read())

        os.remove(input_file)
        os.remove(output_file)
        return response


    return http.HttpResponse("PDF could not be created")
