import os
import datetime

from django.utils.timezone import utc
from django.conf import settings

from sorl.thumbnail import default

from peekaboo.main.models import Visitor, VisitorCount


def recycle_visits(dry_run=False, verbose=False):
    since = (
        datetime.datetime.utcnow().replace(tzinfo=utc) -
        datetime.timedelta(hours=settings.RECYCLE_MINIMUM_HOURS)
    )

    if verbose:
        print "SINCE", repr(since)

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

    default.kvstore.cleanup()
