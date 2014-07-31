from collections import defaultdict

from django.conf import settings
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404

from sorl.thumbnail import get_thumbnail

from peekaboo.main import forms
from peekaboo.main.utils import json_view, non_mortals_required
from peekaboo.main.models import Location, Visitor
from peekaboo.base.utils import ajax_login_required


@non_mortals_required
def home(request):
    data = {}
    data['form'] = forms.SignInForm()
    data['take_picture'] = settings.DEFAULT_TAKE_PICTURE
    return render(request, 'sheet/home.html', data)



@non_mortals_required
def test_photobooth(request):
    return render(request, 'sheet/test_photobooth.html')


@require_POST
@json_view
def signin(request):
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
@ajax_login_required
def upload(request, pk):
    visitor = get_object_or_404(Visitor, pk=pk)
    form = forms.PictureForm(request.POST, request.FILES, instance=visitor)
    if form.is_valid():
        visitor = form.save()
        thumbnail_geometry = request.GET.get('thumbnail_geometry', '100')
        thumbnail = get_thumbnail(
            visitor.picture,
            thumbnail_geometry
        )
        data = {
            'ok': True,
            'thumbnail': {
                'url': thumbnail.url,
                'width': thumbnail.width,
                'height': thumbnail.height,
            }
        }
    else:
        data = {'errors': form.errors}
    return data


@json_view
def locations(request):
    locations = []
    # temporary hack
    if not Location.objects.all().count():
        Location.objects.create(
            name='Mountain View',
            slug='mv',
            timezone='US/Pacific',
        )
    for each in Location.objects.all().order_by('name'):
        locations.append({
            'id': each.pk,
            'name': each.name,
        })
    return {'locations': locations}
