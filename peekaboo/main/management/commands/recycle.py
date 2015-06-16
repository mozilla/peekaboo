from optparse import make_option

from django.db import transaction
from django.core.management.base import BaseCommand

from peekaboo.main.recycle import recycle_visits


class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option(
            '--dry-run',
            action='store_true',
            dest='dry_run',
            default=False,
            help="Run but cancel the whole transaction in the end"
        ),
    )

    def handle(self, dry_run=False, **options):
        verbosity = int(options['verbosity'])
        verbose = verbosity > 1

        # start transaction
        transaction.enter_transaction_management()
        transaction.managed(True)

        recycle_visits(verbose=verbose)

        if dry_run:
            transaction.rollback()
        else:
            transaction.commit()

        transaction.leave_transaction_management()
