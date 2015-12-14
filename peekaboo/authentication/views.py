from django.shortcuts import render


def login(request):
    data = {
        'failed': request.GET.get('bid_login_failed'),
    }
    return render(request, 'authentication/login.html', data)


def logout(request):
    data = {}
    return render(request, 'authentication/login.html', data)
