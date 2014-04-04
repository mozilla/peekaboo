import calendar
import os
import subprocess
import tempfile
import shutil
import stat
import datetime
import time
from collections import defaultdict
from pyquery import PyQuery as pq
from django import http
from django.core.cache import cache
from django.utils.timezone import utc
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.conf import settings
from funfactory.urlresolvers import reverse
from sorl.thumbnail import get_thumbnail
from . import forms
from .models import Visitor, Location, VisitorCount
from .utils import json_view, non_mortals_required
from peekaboo.base.utils import ajax_login_required


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


@non_mortals_required
def log_start(request):
    data = {}
    return render(request, 'main/log-start.html', data)


@non_mortals_required
def log(request, location):
    location = get_object_or_404(Location, slug=location)
    data = {
        'edit_form': forms.SignInForm(),
        'location': location,
    }
    request.session['default-location'] = location.slug
    return render(request, 'main/log.html', data)


@json_view
@non_mortals_required
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
            'modified_iso': visitor.modified.isoformat(),
            'job_title': visitor.job_title,
            'name': visitor.get_name(formal=True),
            'thumbnail': None,
            'visiting': visitor.visiting,
            'company': visitor.company,
        }
        if visitor.picture and os.path.isfile(visitor.picture.path):
            thumbnail = get_thumbnail(
                visitor.picture,
                thumbnail_geometry
            )
            row['thumbnail'] = {
                'url': thumbnail.url,
                'width': thumbnail.width,
                'height': thumbnail.height,
            }
            row['picture_url'] = (
                reverse('main:log_entry_picture', args=(visitor.pk,)) +
                '?width=600&height=400'
            )
        return row

    first = None
    for visitor in recently_created.order_by('-created')[:25]:
        row = make_row(visitor)
        data['created'].append(row)
        if first is None:
            first = max(visitor.created, visitor.modified)
    data['created'].reverse()

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

#    from time import sleep
#    sleep(1)

#    from pprint import pprint
#    pprint(data)
    return data


@json_view
@csrf_exempt
@non_mortals_required
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


@json_view
@csrf_exempt
@non_mortals_required
def log_entry_picture(request, pk, format):
    visitor = get_object_or_404(Visitor, pk=pk)
    if not visitor.picture:
        return http.HttpResponseBadRequest("Doesn't have a picture")

    geometry = (
        '%sx%s' %
        (request.GET.get('width', 600),
         request.GET.get('width', 500))
    )
    picture = get_thumbnail(
        visitor.picture,
        geometry
    )
    return http.HttpResponse(picture.read(), mimetype='image/jpeg')


@login_required
@json_view
@require_POST
@non_mortals_required
def delete_entry(request, pk):
    visitor = get_object_or_404(Visitor, pk=pk)
    visitor.delete()
    # XXX delete all images too??
    return {'deleted': True}


@non_mortals_required
def print_entry(request, pk):
    visitor = get_object_or_404(Visitor, pk=pk)
    data = {
        'visitor': visitor,
        'print': request.GET.get('print', False)
    }
    response = render(request, 'main/print-entry.html', data)
    if request.GET.get('iframe'):
        response['X-Frame-Options'] = 'SAMEORIGIN'
        response["Access-Control-Allow-Origin"] = "*"
    return response


@non_mortals_required
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
            raise IOError("Couldn't find %s (Tried: %s)" % (
                img.attrib['src'],
                source
            ))
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

    _here = os.path.dirname(__file__)
    rasterize_full_path = os.path.join(
        _here,
        'rasterize.js'
    )
    pdf_program = getattr(
        settings,
        'PDF_PROGRAM',
        'phantomjs %s' % rasterize_full_path
    )
    if 'rasterize.js' in pdf_program:
        cmd = (
            pdf_program +
            ' "%(input_file)s"'
            ' "%(output_file)s"'
            ' "10.2cm*5.7cm"'
        )
    elif 'wkpdf' in pdf_program:
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
    #print "CMD"
    #print cmd
    proc = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    out, err = proc.communicate()
    #exit_code = proc.returncode
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
        #response['Content-Disposition'] = (
        #    'filename="%s.pdf"' % os.path.basename(output_file)
        #)
        response = http.HttpResponse(mimetype='application/pdf')
        # so we can print from an iframe
        response['X-Frame-Options'] = 'SAMEORIGIN'
        #response["Access-Control-Allow-Origin"] = "*"
        response.write(open(output_file).read())

        #os.remove(input_file)
        #os.remove(output_file)
        return response

    return http.HttpResponse("PDF could not be created")


@non_mortals_required
def stats_start(request):
    data = {}
    return render(request, 'main/stats-start.html', data)


@non_mortals_required
def stats(request, location):
    location = get_object_or_404(Location, slug=location)
    request.session['default-location'] = location.slug
    rows = []

    _months = defaultdict(int)
    for vc in VisitorCount.objects.all().order_by('year', 'month', 'day'):
        date = datetime.date(vc.year, vc.month, vc.day)
        rows.append({
            'year': vc.year,
            'month': vc.month,
            'day': vc.day,
            'date': date,
            'count': vc.count,
        })
        _month_key = date.strftime('%Y-%m')
        _months[_month_key] += vc.count

    months = []
    for key in sorted(_months.keys()):
        y, m = [int(x) for x in key.split('-')]
        date = datetime.date(y, m, 1)
        months.append({
            'year': date.year,
            'month': date.month,
            'date': date,
            'count': _months[key],
        })

    context = {
        'location': location,
        'days': int(settings.RECYCLE_MINIMUM_HOURS / 24.0),
        'rows': rows,
        'months': months,
    }

    return render(request, 'main/stats.html', context)


def debugger(request):
    r = http.HttpResponse()
    r.write('absolute_uri: %s\n' % request.build_absolute_uri())
    r.write('DEBUG: %s\n\n' % settings.DEBUG)
    if request.is_secure():
        r.write('request.is_secure()\n')
        r.write(
            'Expect SITE_URL to contain HTTPS: %s\n' % (
                settings.SITE_URL,
            )
        )
        r.write(
            'Expect SESSION_COOKIE_SECURE to be True: %s\n' % (
                settings.SESSION_COOKIE_SECURE,
            )
        )
    else:
        r.write('NOT request.is_secure()\n')
        r.write(
            'Expect SITE_URL to contain HTTP: %s\n' % (
                settings.SITE_URL,
            )
        )
        r.write(
            'Expect SESSION_COOKIE_SECURE to be False: %s\n' % (
                settings.SESSION_COOKIE_SECURE,
            )
        )

    if cache.get('foo'):
        r.write('\nCache seems to work!\n')
    else:
        r.write('\nReload to see if cache works\n')
        cache.set('foo', 'bar', 60)
    r['content-type'] = 'text/plain'
    return r
