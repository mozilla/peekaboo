import sys

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):

    args = 'emailaddresses'

    def handle(self, *emails, **options):
        if not emails:
            print >>sys.stderr, "No email addresses supplied"
            return
        for email in emails:
            user, __ = User.objects.get_or_create(
                email__iexact=email
            )
            print email.ljust(40),
            if user.is_superuser:
                print "Was already superuser"
            else:
                print "Now a superuser"
                user.is_superuser = True
                user.save()
