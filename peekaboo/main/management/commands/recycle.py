import datetime
import os
from optparse import make_option

from django.utils.timezone import utc
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import transaction

from sorl.thumbnail import default

from peekaboo.main.models import Visitor, VisitorCount


class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option('--dry-run', action='store_true', dest='dry_run', default=False,
                    help="Run but cancel the whole transaction in the end"),
    )

    def handle(self, dry_run=False, **options):
        verbosity = int(options['verbosity'])
        verbose = verbosity > 1
        since = (
            datetime.datetime.utcnow().replace(tzinfo=utc) -
            datetime.timedelta(hours=settings.RECYCLE_MINIMUM_HOURS)
        )

        if verbose:
            print "SINCE", repr(since)

        # start transaction
        transaction.enter_transaction_management()
        transaction.managed(True)

        count = 0
        for visitor in Visitor.objects.filter(created__lt=since):
            if verbose:
                print "DELETE", repr(visitor.get_name())

            VisitorCount.create_from_visitor(visitor)
            if visitor.picture:
                if verbose:
                    if os.path.isfile(visitor.picture.path):
                        print "DELETING", visitor.picture.path
                visitor.picture.delete()
            visitor.delete()
            count += 1

        if verbose:
            print "\nIN SUMMARY".ljust(70, '=')
            print count, "visitor records deleted"
            print "\n"
        if dry_run:
            transaction.rollback()
        else:
            transaction.commit()

        transaction.leave_transaction_management()

        default.kvstore.cleanup()
