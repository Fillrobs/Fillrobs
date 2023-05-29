#!/usr/local/bin/python

from utilities.mail import email_admin

"""
django-admin command for sending an email to the address defined in GlobalPreferences.admin_email. This is useful for
the upgrader to call to notify users on success/failure of the upgrade.
"""
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "-s",
            "--subject",
            help="Subject line for the email",
            dest="subject",
            required=True,
        )
        parser.add_argument(
            "-m",
            "--message",
            help="Message body of the email",
            dest="message",
            required=True,
        )

    def handle(self, subject, message, *args, **options):
        email_admin(context={"subject": subject, "message": message})
