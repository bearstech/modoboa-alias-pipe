import sys
import os.path
import csv
from optparse import make_option

from modoboa.core.models import User
from django.core.management.base import BaseCommand


from modoboa.core import load_core_settings
from modoboa.core.management.commands import CloseConnectionMixin
from modoboa.lib.exceptions import Conflict
from modoboa_alias_pipe.views import import_alias_pipe

from modoboa.core.extensions import exts_pool


class Command(BaseCommand, CloseConnectionMixin):
    args = 'csvfile'
    help = 'Import alias commands csv file'

    option_list = BaseCommand.option_list + (
        make_option(
            '--sepchar', action='store_true', dest='sepchar', default=';'
        ),
        make_option(
            '--continue-if-exists', action='store_true',
            dest='continue_if_exists', default=True
        )
    )

    def handle(self, *args, **kwargs):
        superadmin = User.objects.filter(is_superuser=True).first()
        exts_pool.load_all()
        load_core_settings()

        for filename in args:
            if not os.path.exists(filename):
                print('File not found')
                sys.exit(1)

            with open(filename, 'r') as f:
                reader = csv.reader(f, delimiter=';')
                for row in reader:
                    if not row:
                        continue

                    print(row)
                    try:
                        import_alias_pipe(superadmin, row, kwargs)
                    except Conflict:
                        if kwargs['continue_if_exists']:
                            continue

                        raise Conflict(
                            "Object already exists: %s"
                            % kwargs['sepchar'].join(row[:2])
                        )
