from nose.tools import eq_, ok_

from django.contrib.auth.models import User
from django.conf import settings

from funfactory.urlresolvers import reverse
from peekaboo.main.tests.test_views import BaseTestCase


class TestViews(BaseTestCase):

    def test_home_page(self):
        url = reverse('users:home')
        response = self.client.get(url)
        eq_(response.status_code, 302)
        ok_(settings.LOGIN_URL in response['location'])

        bob = User.objects.create(username='bob', email='bob@example.com')

        self._login(is_superuser=True)
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
