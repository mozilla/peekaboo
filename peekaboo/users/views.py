from django.shortcuts import render, redirect
from django.contrib.auth.models import User

from peekaboo.base.utils import superuser_required


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
