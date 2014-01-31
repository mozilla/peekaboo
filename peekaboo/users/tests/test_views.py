from nose.tools import eq_, ok_

from django.test import TestCase
from django.contrib.auth.models import User
from django.conf import settings

from funfactory.urlresolvers import reverse


class TestViews(TestCase):

    def _login(self, is_staff=False, is_superuser=True):
        user, __ = User.objects.get_or_create(
            username='shannon',
            email='shannon@mozilla.com',
        )
        user.is_staff = is_staff
        user.is_superuser = is_superuser
        user.set_password('secret')
        user.save()
        assert self.client.login(username='shannon', password='secret')
        return user

    def test_home_page(self):
        url = reverse('users:home')
        response = self.client.get(url)
        eq_(response.status_code, 302)
        ok_(settings.LOGIN_URL in response['location'])

        bob = User.objects.create(username='bob', email='bob@example.com')

        user = self._login()
        response = self.client.get(url)
        eq_(response.status_code, 200)

        ok_('bob@example.com' in response.content)

        response = self.client.post(url, {'staff': bob.pk})
        eq_(response.status_code, 302)
        bob = User.objects.get(pk=bob.pk)
        ok_(bob.is_staff)

        response = self.client.post(url, {'staff': bob.pk})
        eq_(response.status_code, 302)
        bob = User.objects.get(pk=bob.pk)
        ok_(not bob.is_staff)

        response = self.client.post(url, {'superuser': bob.pk})
        eq_(response.status_code, 302)
        bob = User.objects.get(pk=bob.pk)
        ok_(bob.is_superuser)

        response = self.client.post(url, {'superuser': bob.pk})
        eq_(response.status_code, 302)
        bob = User.objects.get(pk=bob.pk)
        ok_(not bob.is_superuser)
