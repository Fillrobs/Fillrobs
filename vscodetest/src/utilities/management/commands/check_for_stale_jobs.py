#!/usr/local/bin/python
from __future__ import unicode_literals

import os
import sys
import datetime

from django.core.management.base import BaseCommand

from utilities.logger import ThreadLogger
from utilities.mail import email, email_admin

os.environ["DJANGO_SETTINGS_MODULE"] = "settings"

logger = ThreadLogger(__name__)


class Command(BaseCommand):

    help = (
        "Check CloudBolt db for any stale jobs; i.e. jobs that have been running for more "
        "than RUNTIMELIMIT minutes (defaults to a day)"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "-t",
            "--runtimelimit",
            default=(60 * 24),
            help=(
                "Runtime limit after which jobs are considered stale, in minutes [%default]"
            ),
        )
        parser.add_argument(
            "-e",
            "--emails",
            help=(
                "Comma separated list of emails to send job list to, if none "
                "specified, all cbadmins will be emailed"
            ),
        )
        parser.add_argument(
            "-c",
            "--cancel",
            action="store_true",
            help="If specified it will cancel any job found, removing lock files where applicable",
        )
        parser.add_argument(
            "-n",
            "--noemail",
            action="store_true",
            help=(
                "When specified in conjunction with '-c' will silently cancel jobs without "
                "emailing anyone about it."
            ),
        )

    def cancel_stale_jobs(self, jobs, delta):
        # this only sets the status to canceled and deletes a lock file if one exists.  Currently
        # there is no way to actually stop a thread if one is activelly running.  This is however
        # sufficient for the truly stale jobs use case.
        from django.conf import settings

        for job in jobs:
            job.set_progress(
                "Canceled because job exceeded runtime limit of {} minutes".format(
                    delta
                ),
                1,
                1,
            )
            job.status = "CANCELED"
            job.save()
            if job.type == "syncvms":
                rhs = job.job_parameters.cast().resource_handlers.all()
                if len(rhs) == 1:
                    lockfile_name = "syncvms-{}.lock".format(rhs[0].id)
                    lockfile_path = os.path.join(settings.LOCKFILES_DIR, lockfile_name)
                    if os.path.exists(lockfile_path):
                        os.unlink(lockfile_path)

    def email_failure_message(self, body_text, jobs, emails):
        """
        Send a report of the failure to emails. If not specified,
        it is sent to every CB admin.
        """
        email_kwargs = {
            "email_context": {"body_text": body_text, "jobs": jobs},
            "slug": "stale-job-report",
            "continue_on_error": True,
        }
        if emails:
            email(recipients=emails.split(","), **email_kwargs)
        else:
            email_admin(**email_kwargs)

    def handle(self, *args, **options):
        delta = int(options["runtimelimit"])

        # earliest valid start time
        valid_start_time = datetime.datetime.now() - datetime.timedelta(minutes=delta)

        from jobs.models import Job

        stale_jobs = Job.objects.filter(
            status__in=["RUNNING", "QUEUED"], start_date__lt=valid_start_time
        ).all()

        if stale_jobs:
            emails = options["emails"]
            prefix = "Found"
            if options.get("cancel"):
                prefix += " and canceled"
                self.cancel_stale_jobs(stale_jobs, delta)
            msg = "{} {} stale jobs.".format(prefix, len(stale_jobs))
            logger.info(msg)
            if not options.get("noemail"):
                self.email_failure_message(msg, stale_jobs, emails)
            sys.exit(0)
        else:
            logger.info("No stale jobs found")
        sys.exit(0)
