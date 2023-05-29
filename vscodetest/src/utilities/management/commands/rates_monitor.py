#!/usr/local/bin/python
from __future__ import unicode_literals
from __future__ import print_function

"""
Management command to monitor the rates system for discrepancies. Returns an
error if there is a discrepancy.
"""

import os
import sys

from django.core.management.base import BaseCommand
from django.utils.translation import ugettext as _

from costs.rectifier import rate_rectifier
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
            help=(
                "Comma separated list of group names to "
                "target (default: all of them)"
            ),
        )
        parser.add_argument(
            "-e",
            "--environments",
            help=(
                "Comma separated list of environment names "
                "to target (default: all of them)"
            ),
        )
        parser.add_argument(
            "-n", "--noemail", action="store_true", help="Do not send emails"
        )
        parser.add_argument(
            "-f",
            "--fail",
            action="store_true",
            help=(
                "Fail immediately and exit non zero when an error "
                "is found. Implies --watch"
            ),
        )
        parser.add_argument(
            "-w", "--watch", action="store_true", help="Run the rectifier continually"
        )
        parser.add_argument(
            "-q",
            "--quiet",
            action="store_true",
            help="Quiet output, same as --verbosity 0",
        )

    def handle(self, *args, **options):
        """
        Main entry point for this management command
        """
        fail = options.get("fail")
        watch = options.get("watch")
        # default verbosity is 1
        verbose = int(options.get("verbosity"))
        quiet = options.get("quiet")

        # fail implies watch
        if fail:
            watch = True
        # quiet implies verbosity 0
        if quiet:
            verbose = 0

        errors = 0
        while not errors or not fail:
            errors = rate_rectifier(
                rectify=options.get("rectify"),
                verbose=verbose,
                groups=options.get("groups"),
                environments=options.get("environments"),
            )

            if not watch:
                break
            elif verbose > 1:
                print()  # separate this round of rectifying from others
            elif verbose and not errors:
                sys.stdout.write(".")
                sys.stdout.flush()

        if errors:
            msg = "Discrepancies found in the rates on the following servers:\n\n"
            msg += "\n".join([s.hostname for s in errors])
            logger.error(msg)
        else:
            logger.info("No rate discrepancies found")

        # send emails
        if not options.get("noemail") and errors:
            emails = options.get("emails")
            email_failure_message(errors, emails)

        sys.exit(len(errors))


def email_failure_message(errors, emails):
    """
    Send a report of the failure to emails. If not specified,
    it is sent to every CB admin.
    """
    body_text = _("Discrepancies found in the rates on the following servers:\n\n")
    body_text += "\n".join([s.hostname for s in errors])

    email_context = {"message": body_text, "subject": _("Rates monitor failure")}
    try:
        if emails:
            email_list = emails.split(",")
            # subject, body, sender, recipients
            email(recipients=email_list, slug="job-failure", context=email_context)
        else:  # email cb admins set in global preferences
            email_admin(slug="job-failure", context=email_context)
    except Exception as err:
        msg = "Unable to send the failure e-mail. Exception: %s" % err
        logger.exception(msg)
