#!/usr/local/bin/python
from __future__ import unicode_literals, print_function

"""
Management command to add rate deltas to all ServerHistory events in 9.0.1.

Does not add rate deltas to ResourceHistory events, but it could be made to do that if needed.
"""
import datetime
import sys

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Q

from common.methods import is_version_newer
from history.models import ServerHistory
from infrastructure.models import Server


def should_run_command():
    # get the current version
    version = settings
    attributes = ["VERSION_INFO", "VERSION"]
    for attr in attributes:
        if isinstance(version, dict):
            version = version.get(attr)
        else:
            version = getattr(version, attr, None)
        if not version:
            # must be a really old version as pre-dates the format change to settings.VERSION_INFO
            return False

    # at this point version is the correct version string representation
    if version == "dev":
        # 'dev' is never 'newer' by definition, but it helps development to consider it valid in
        # this particular case
        return True

    # If the version is older than 9.0.1, return False as the command should only run in 9.0.1 and newer
    return not is_version_newer("9.0.1", version)


def add_rate_changes(server, dry_run=False):
    """
    Iterate over the history events for the given server and add a value for the rate_change.
    """
    events = (
        ServerHistory.objects.filter(server=server)
        .filter(
            event_type__in=[
                "CREATION",
                "ONBOARD",
                "MODIFICATION",
                "DECOMMISSION",
                "RATE",
            ]
        )
        .order_by("action_time")
    )
    total_rate_of_previous_event = 0
    for event in events:
        if event.total_rate is None:
            # skip any events where the total_rate is not set
            event.rate_change = 0
        else:
            event.rate_change = event.total_rate - total_rate_of_previous_event
            total_rate_of_previous_event = event.total_rate
        if not dry_run:
            event.save()


def get_servers_to_process(options):
    delta = int(options["days"])
    # earliest valid event.action_time
    earliest_valid_event_time = datetime.datetime.now() - datetime.timedelta(days=delta)

    # Filter to servers that have had history events in the last time period
    servers_with_history_events = Server.objects.filter(
        Q(serverhistory__action_time__lte=earliest_valid_event_time)
        | Q(status="ACTIVE")
    ).distinct()
    if options["ids"]:
        ids_to_filter = options["ids"].split(",")
        print(f'Limiting servers to just ID(s) {", ".join(ids_to_filter)}.')
        servers_with_history_events = servers_with_history_events.filter(
            id__in=ids_to_filter
        )
    return servers_with_history_events


class Command(BaseCommand):

    help = (
        "Revise hardware rates on the ServerHistory records to adjust for a bug resolved in v8.4"
        "It only updates records created in the last 60 days, to change the default "
        "use the -d flag"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "-d",
            "--days",
            default=60,
            help=(
                "Update all appropriate records created in the last NUMBER_OF_DAYS days"
            ),
        )
        parser.add_argument(
            "-i",
            "--ids",
            default=None,
            help=("Limit Servers to the IDs in the provided, comma-separated list"),
        )
        parser.add_argument(
            "-dry",
            "--dryrun",
            action="store_true",
            help=("Don't save rate changes to the database"),
        )

    def handle(self, *args, **options):
        if not should_run_command():
            print(
                "This management command is not expected to run for versions older than 8.3."
            )
            sys.exit(3)

        servers_with_history_events = get_servers_to_process(options)
        total_servers = servers_with_history_events.count()
        print(
            "Adding rate change values to the history events for {} server(s).".format(
                total_servers
            )
        )

        for i, server in enumerate(servers_with_history_events):
            if i % 10 == 0:
                print(f"Processing server {i + 1} / {total_servers}.")
            add_rate_changes(server, dry_run=options["dryrun"])

        print("Done adding rates.")
