#!/usr/local/bin/python
from __future__ import unicode_literals

"""
django-admin command for running trigger action jobs.

For example:
    ./manage.py execute_rules
"""


from django.core.management.base import BaseCommand

import sys
import logging
from cbhooks.models import TriggerPoint
from cbhooks.views import there_are_active_triggers, create_pending_trigger_job
from utilities.logger import ThreadLogger

logger = ThreadLogger(__name__)


def configure_logging(filename):
    """
    Configure the logger such that all run-time output, either emitted directly
    from this script or indirectly via the CloudBolt machinery, is captured
    *here* and does not pollute the application logs.
    """
    if filename:
        # Direct all output to the specified file
        handler = logging.handlers.RotatingFileHandler(
            filename, mode="a", maxBytes=1024 * 1024, backupCount=3
        )
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        )
        level = logging.DEBUG  # Capture debug output during the cron job

    else:
        # Direct all output to the console
        handler = logging.StreamHandler(stream=sys.stdout)
        formatter = logging.Formatter("%(message)s")
        level = logging.INFO  # Minimize debug output on the console

    handler.setLevel(level)
    handler.setFormatter(formatter)

    # Configure the top-level (root) logger with these settings
    logger.handlers = []  # @@disable handlers inherited from settings.py
    logger.setLevel(level)

    # FIXME for some reason adding this handler will print log messages twice,
    # so for now just adding it when a specific log file is requested:
    if filename:
        logger.addHandler(handler)

    return


class Command(BaseCommand):
    help = """Checks whether any enabled rules have enabled conditions and actions
    and spawns jobs to run them if necessary.

Examples:
  python manage.py execute_rules

    """

    def handle(self, *args, **options):
        if len(args) > 0:
            trigger_point_id = int(args[0])
        else:
            trigger_point_id = None

        num_enabled_rules = 1
        if not trigger_point_id:
            num_enabled_rules = TriggerPoint.objects.filter(enabled=True).count()
            num_disabled_rules = TriggerPoint.objects.filter(enabled=False).count()
            if num_enabled_rules > 0:
                logger.info(
                    "Executing {} enabled rules ({} disabled rules "
                    "will not be checked)".format(num_enabled_rules, num_disabled_rules)
                )

        if num_enabled_rules > 0 and there_are_active_triggers(trigger_point_id):
            trigger_job = create_pending_trigger_job(trigger_point_id)

            job_id = trigger_job.id
            logfile = trigger_job.get_log_file_path()
            logger.info("Created job: %s" % job_id)
            logger.info("Job log file: %s" % logfile)
        elif num_enabled_rules > 0:
            if trigger_point_id:
                logger.info("No active triggers found for selected rule")
            else:
                logger.info("No enabled rules with active triggers found")
        else:
            logger.info("There are no enabled rules to execute")
        logger.info("Exiting")
