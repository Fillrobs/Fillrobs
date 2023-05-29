#!/usr/local/bin/python
from __future__ import unicode_literals

"""
Used by upgrade_cloudbolt.sh to prevent accidental downgrades

Exits with status 0 if the first version provided is newer than the second, exits with status 3
otherwise.

We use status code 3 because 1 and 2 are taken: code 1 is an error, and code 2
is invalid input (such as incorrect number of args).
"""

import sys
from django.core.management.base import BaseCommand

from common.methods import is_version_newer


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("v1")
        parser.add_argument("v2")

    def handle(self, v1, v2, *args, **options):
        if is_version_newer(v1, v2):
            # print "{} is newer than {}".format(v1, v2)
            sys.exit(0)
        else:
            # print "{} is not newer than {}".format(v1, v2)
            sys.exit(3)
