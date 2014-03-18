from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User

from peekaboo.base.utils import superuser_required
from peekaboo.main.models import Location
from . import forms


@superuser_required
def home(request):
    context = {}
    if request.method == 'POST':
        raise NotImplementedError
        if request.POST.get('staff'):
            user = User.objects.get(pk=request.POST.get('staff'))
            user.is_staff = not user.is_staff
            user.save()
        if request.POST.get('superuser'):
            user = User.objects.get(pk=request.POST.get('superuser'))
            user.is_superuser = not user.is_superuser
            user.save()
        return redirect('users:home')

    locations = Location.objects.all().order_by('name')
    context['locations'] = locations
    return render(request, 'locations/home.html', context)


@superuser_required
def edit(request, pk):
    location = get_object_or_404(Location, pk=pk)
    if request.method == 'POST':
        form = forms.LocationForm(request.POST, instance=location)
        if form.is_valid():
            form.save()
            return redirect('locations:home')
    else:
        form = forms.LocationForm(instance=location)
    context = {
        'form': form,
        'location': location,
    }
    return render(request, 'locations/edit.html', context)


@superuser_required
def new(request):
    if request.method == 'POST':
        form = forms.LocationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('locations:home')
    else:
        form = forms.LocationForm()
    context = {
        'form': form,
    }
    return render(request, 'locations/edit.html', context)
