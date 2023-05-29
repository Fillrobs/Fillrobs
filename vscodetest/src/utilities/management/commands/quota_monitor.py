#!/usr/local/bin/python
from __future__ import unicode_literals

"""
Management command to monitor quotas. Returns an error if there is a
discrepancy in the quota system.
"""

import os
import sys

from django.core.management.base import BaseCommand
from django.utils.translation import ugettext as _

from accounts.models import Group
from infrastructure.models import Environment

from quota.rectifier import first_run
from utilities.logger import ThreadLogger
from utilities.mail import email, email_admin

os.environ["DJANGO_SETTINGS_MODULE"] = "settings"

logger = ThreadLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "-m",
            "--emails",
            help=(
                "Comma separated list of emails to "
                "send failure messages to, if none "
                "specified, all cbadmins will be emailed"
            ),
        )
        parser.add_argument(
            "-r",
            "--rectify",
            action="store_true",
            help="If a failure is found, rectify the discrepancy",
        )
        parser.add_argument(
            "-g",
            "--groups",
            help="Comma separated list of group names to target (default: all of them)",
        )
        parser.add_argument(
            "-e",
            "--environments",
            help="Comma separated list of environment names to target (default: all of them)",
        )
        parser.add_argument(
            "-n", "--noemail", action="store_true", help="Do not send emails"
        )

    def email_failure_message(self, body_text, emails):
        """
        Send a report of the failure to emails. If not specified,
        it is sent to every CB admin.
        """
        email_context = {"message": body_text, "subject": _("Quota Monitor failure")}
        try:
            if emails:
                email_list = emails.split(",")
                # subject, body, sender, recipients
                email(recipients=email_list, slug="job-failure", context=email_context)
            else:  # email cb admins set in global preferences
                email_admin(slug="job-failure", context=email_context)
        except Exception as err:
            msg = _("Unable to send the failure e-mail. Exception: {error}").format(
                error=err
            )
            logger.warning(msg)

    def handle(self, *args, **options):
        groups = options.get("groups", None)
        if groups:
            group_names = groups.split(",")
            groups = list(Group.objects.filter(name__in=group_names))

        environments = options.get("environments")
        if environments:
            environment_names = environments.split(",")
            environments = list(Environment.objects.filter(name__in=environment_names))

        rect = first_run(
            dry_run=True, transfer_limits=True, groups=groups, environments=environments
        )
        if rect[0]:
            rect = rect[1].replace("\\n", "\n")
            logger.error(rect)
            emails = options["emails"]
            if options.get("rectify"):
                # fix quotas for the selected groups & envs
                first_run(
                    dry_run=False,
                    transfer_limits=True,
                    groups=groups,
                    environments=environments,
                )
                logger.info("Quotas successfully rectified")
            if not options.get("noemail"):
                self.email_failure_message(rect, emails)
            sys.exit(1)
        else:
            logger.info("No quota discrepancies found")
            # uncomment these lines to get more info when t-shooting quota discrepancies
            # rect = rect[1].replace('\\n', '\n')
            # logger.info(rect)
