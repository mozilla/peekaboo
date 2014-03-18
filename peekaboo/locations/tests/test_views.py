from nose.tools import eq_, ok_

from django.conf import settings

from funfactory.urlresolvers import reverse

from peekaboo.main.tests.test_views import BaseTestCase
from peekaboo.main.models import Location


class TestViews(BaseTestCase):

    def test_home_page(self):
        url = reverse('locations:home')
        response = self.client.get(url)
        eq_(response.status_code, 302)
        ok_(settings.LOGIN_URL in response['location'])

        location = Location.objects.create(
            name='Mountain View',
            slug='mv',
            timezone='US/Pacific'
        )

        self._login(is_superuser=True)
        response = self.client.get(url)
        eq_(response.status_code, 200)

        ok_('Mountain View' in response.content)
        edit_url = reverse('locations:edit', args=(location.pk,))
        ok_(edit_url in response.content)

    def test_edit_location(self):
        location = Location.objects.create(
            name='Mountain View',
            slug='mv',
            timezone='US/Pacific'
        )
        url = reverse('locations:edit', args=(location.pk,))
        self._login(is_superuser=True)
        response = self.client.get(url)
        eq_(response.status_code, 200)

        post_data = dict(
            name='London',
            slug='london',
            timezone='Europe/London'
        )
        response = self.client.post(url, post_data)
        eq_(response.status_code, 302)

        location = Location.objects.get(pk=location.pk)
        eq_(location.name, 'London')
        eq_(location.slug, 'london')
        eq_(location.timezone, 'Europe/London')

    def test_new_location(self):
        url = reverse('locations:new')
        self._login(is_superuser=True)
        response = self.client.get(url)
        eq_(response.status_code, 200)

        post_data = dict(
            name='London',
            slug='london',
            timezone='Europe/London'
        )
        response = self.client.post(url, post_data)
        eq_(response.status_code, 302)

        Location.objects.get(
            name='London',
            slug='london',
            timezone='Europe/London'
        )
