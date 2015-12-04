# -*- coding: utf-8 -*-

import os
import datetime
import json

from nose.tools import eq_, ok_

from django.test import TestCase, Client
from django.conf import settings
from django.contrib.auth.models import User

from funfactory.urlresolvers import reverse, split_path

from peekaboo.main.models import Location, Visitor


class LocalizingClient(Client):
    """Client which prepends a locale so test requests can get through
    LocaleURLMiddleware without resulting in a locale-prefix-adding 301.

    Otherwise, we'd have to hard-code locales into our tests everywhere or
    {mock out reverse() and make LocaleURLMiddleware not fire}.
    """

    def request(self, **request):
        """Make a request, but prepend a locale if there isn't one already."""
        # Fall back to defaults as in the superclass's implementation:
        path = request.get('PATH_INFO', self.defaults.get('PATH_INFO', '/'))
        locale, shortened = split_path(path)
        if not locale:
            request['PATH_INFO'] = '/%s/%s' % (settings.LANGUAGE_CODE,
                                               shortened)
        return super(LocalizingClient, self).request(**request)


class BaseTestCase(TestCase):

    client_class = LocalizingClient

    def _login(self, is_staff=True, is_superuser=False):
        user, __ = User.objects.get_or_create(
            username='shannon',
            email='shannon@mozilla.com',
        )
        if is_superuser:
            is_staff = True
        user.is_staff = is_staff
        user.is_superuser = is_superuser
        user.set_password('secret')
        user.save()
        assert self.client.login(username='shannon', password='secret')
        return user


class TestViews(BaseTestCase):

    def test_contribute_json(self):
        response = self.client.get('/contribute.json')
        eq_(response.status_code, 200)
        # should be valid JSON
        ok_(json.loads(response.content))
        eq_(response['Content-Type'], 'application/json')

    def test_log_entries(self):
        location = Location.objects.create(
            name='Mountain View',
            slug='mv',
            timezone='US/Pacific',
        )

        url = reverse('main:log_entries', args=('mv',))
        response = self.client.get(url)
        eq_(response.status_code, 302)

        self._login()
        response = self.client.get(url)
        eq_(response.status_code, 200)
        data = json.loads(response.content)
        eq_(data['created'], [])
        eq_(data['latest'], None)

        # add an entry
        visitor1 = Visitor.objects.create(
            location=location,
            first_name='Bill',
            last_name='Gates',
            job_title='Boss',
        )

        response = self.client.get(url)
        eq_(response.status_code, 200)
        data = json.loads(response.content)
        eq_(len(data['created']), 1)
        eq_(data['created'][0]['name'], 'Bill Gates')
        eq_(data['created'][0]['job_title'], 'Boss')
        eq_(data['created'][0]['id'], visitor1.pk)

        ok_(isinstance(data['latest'], int))
        # this number should be a
        latest_timestamp = data['latest']
        latest = datetime.datetime.utcfromtimestamp(latest_timestamp)
        # this won't contain a timezone but the hour and minute should
        # be the same as the `visitor1`
        eq_(
            visitor1.created.strftime('%H:%M'),
            latest.strftime('%H:%M')
        )
        # include this and nothing new should come
        response = self.client.get(url, {
            'latest': str(latest_timestamp),
        })
        eq_(response.status_code, 200)
        data = json.loads(response.content)
        eq_(data['created'], [])
        eq_(data['modified'], [])
        eq_(data['latest'], None)

        # let's add another, newer
        visitor2 = Visitor.objects.create(
            location=location,
            first_name='Paul',
            last_name='Allen',
        )
        visitor2.created += datetime.timedelta(seconds=1)
        visitor2.save()

        response = self.client.get(url, {
            'latest': str(latest_timestamp),
        })
        eq_(response.status_code, 200)
        data = json.loads(response.content)
        eq_(len(data['created']), 1)
        eq_(data['created'][0]['name'], 'Paul Allen')
        eq_(data['created'][0]['id'], visitor2.pk)

        new_latest_timestamp = data['latest']
        # this won't contain a timezone but the hour and minute should
        # be the same as the `visitor1`
        eq_(latest_timestamp + 1, new_latest_timestamp)

        # ask one more time and nothing new should come back
        previous_latest = data['latest']
        response = self.client.get(url, {
            'latest': previous_latest,
        })
        eq_(response.status_code, 200)
        data = json.loads(response.content)
        eq_(len(data['created']), 0)
        eq_(len(data['modified']), 0)

        # let's modify the first visitor
        visitor1.job_title = 'Philantropist'
        visitor1.modified += datetime.timedelta(seconds=10)
        visitor1.save()

        response = self.client.get(url, {
            'latest': previous_latest,
        })
        eq_(response.status_code, 200)
        data = json.loads(response.content)
        eq_(len(data['modified']), 1)

        previous_latest_timestamp = new_latest_timestamp
        new_latest_timestamp = data['latest']
        eq_(
            previous_latest_timestamp + 10 - 1,
            new_latest_timestamp
        )
        response = self.client.get(url, {
            'latest': str(new_latest_timestamp),
        })
        eq_(response.status_code, 200)
        data = json.loads(response.content)
        eq_(data['created'], [])
        eq_(data['modified'], [])
        eq_(data['latest'], None)

    def test_eventbrite_upload(self):

        url = reverse('main:csv_upload')
        response = self.client.get(url)
        eq_(response.status_code, 302)

        self._login()
        response = self.client.get(url)
        eq_(response.status_code, 200)

        location = Location.objects.create(
            name='Berlin',
            slug='berlin',
            timezone='Europe/Berlin',
        )
        _here = os.path.dirname(__file__)
        response = self.client.post(url, {
            'file': open(os.path.join(_here, 'sample-eventbrite.csv')),
            'format': 'eventbrite',
            'location': location.id,
            'date': '2015-06-16 13:00:00',  # Europe summer time, is +2h
        })

        visitors = Visitor.objects.filter(location=location)
        first_names = [x.first_name for x in visitors.order_by('first_name')]
        eq_(first_names, [u'Nicolai Froehlich', u'Södan'])
        first_created = [x.created for x in visitors][0]
        eq_(first_created.strftime('%H:%M %Z'), '11:00 UTC')
