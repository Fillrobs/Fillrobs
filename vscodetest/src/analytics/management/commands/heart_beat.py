"""
A script meant to be called by a scheduler. Each call reports a heart beat.
"""
from __future__ import unicode_literals

from pprint import pprint

import urllib3

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from mixpanel import Mixpanel

from common.methods import set_proxy_env_vars
from utilities.logger import ThreadLogger

MIXPANEL_TOKEN = settings.MIXPANEL_TOKEN

logger = ThreadLogger(__name__)
http = urllib3.PoolManager()


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            default=False,
            action="store_true",
            help="Do not submit heart beat data; only print it.",
        )
        parser.add_argument(
            "--facts-fail-heart-beat",
            default=False,
            action="store_true",
            help="Facts, if they raise an Exception, will cause heart_beat to exit 1.",
        )

    def handle(self, *args, **options):
        reraise_on_fact_exceptions = False
        if "facts_fail_heart_beat" in options and options["facts_fail_heart_beat"]:
            reraise_on_fact_exceptions = True

        # Import the latest heart_beat_facts, triggering a possible recompile.
        from analytics import heart_beat_facts

        properties = heart_beat_facts.repo.facts(reraise_on_fact_exceptions)

        if options["dry_run"]:
            pprint(properties)
        else:
            set_proxy_env_vars()
            mp = Mixpanel(MIXPANEL_TOKEN)

            # the distinct_id should *always* be the bios ID, but for testing
            # with our dev environments, we'll accept the file system id as an
            # alternative (non-root users typically can access bios id).
            distinct_id = properties.get("id.bios") or properties["id.file system"]

            try:
                mp.track(distinct_id, "heart beat", properties)
            except Exception as err:
                error_msg = "Failed to send heart beat event to Mixpanel"
                logger.exception(error_msg)
                error_msg += ": {}".format(err)
                raise CommandError(error_msg)
