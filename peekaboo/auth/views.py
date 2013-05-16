from django.conf import settings
#from django.views.decorators.http import require_POST
#from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render


def login(request):
    data = {}
    return render(request, 'auth/login.html', data)


def logout(request):
    data = {}
    return render(request, 'auth/login.html', data)
