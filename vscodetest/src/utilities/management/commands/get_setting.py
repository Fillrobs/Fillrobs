#!/usr/local/bin/python
from __future__ import unicode_literals, print_function

"""
django-admin command for retrieving a setting value from settings.py

Used by shell scripts that need to fetch Django configuration settings (ex.
upgrade_cloudbolt.sh needs to look under the VARDIR for a jobengine.lock file)
"""
import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "-s",
            "--setting-name",
            help="Name of the setting to fetch. Ex. DEBUG, VARDIR",
            dest="settingname",
            required=True,
        )

    def handle(self, *args, **options):
        print(getattr(settings, options["settingname"]))
