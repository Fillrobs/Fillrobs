"""
Generates configuration for the frontend webserver instance.

The current implementation is apache2 so this command regenerates a portion of the
apache2 configuration. This command sources configuration from user configurable options currently in
GlobalPreferences . This is intended to reduce user tweaks performed directly in the apache2 configuration files
by exposing common options required in the GUI to reduce complexity
for the end user and allow us to perform sanity checks on the configuration before it is applied.
"""
from __future__ import unicode_literals

from django.core.management.base import BaseCommand

from utilities.helpers import generate_apache2_conf


class Command(BaseCommand):
    def handle(self, *args, **options):
        generate_apache2_conf()
