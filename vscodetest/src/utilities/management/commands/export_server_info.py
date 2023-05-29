#!/usr/local/bin/python
from __future__ import unicode_literals
from __future__ import print_function

"""
django-admin command for exporting server field values in CSV format

For example, this exports a list hostnames and CPU counts for all servers
belonging to the HR or IT groups:
    ./manage.py export_server_info -g HR,IT -f hostname,cpu_cnt

Dev Notes
=========
  - User story: https://cloudbolt.atlassian.net/browse/DEV-367
  - writes over existing output files without warning
    string.
"""
from builtins import range
from builtins import object

from csv import writer as make_csv_writer
from decimal import Decimal  # for type-checking
from sys import stderr, exit
from tempfile import TemporaryFile

from django.core.management.base import BaseCommand

from accounts.models import Group
from infrastructure.models import Server, CustomField
from common.methods import mkDateTime, last_month_day_info
from resourcehandlers.vmware.models import VmwareServerInfo
from utilities.mail import email


class Report(object):
    def __init__(
        self, servers, field_list, start_period=None, end_period=None, use_stdout=False
    ):
        """
        Create a report for the servers in `servers` with data for the fields
        in `field_list`. The report is written to the `csv` attribute.

        A report needs to be written or routed somewhere for the user's
        consumption. Functions that do that include `export_as_named_file` and
        `export_as_email`.

        Start period and end period only effect the field "hours_on"
        """
        file_ = TemporaryFile(mode="w+t")
        writer = make_csv_writer(file_)

        # translate the CF names in field_list to friendlier CF labels
        cfs = CustomField.objects.filter(name__in=field_list)
        name_to_label = {cf.name: cf.label for cf in cfs}
        label_list = [
            name_to_label.get(field_name, field_name) for field_name in field_list
        ]

        # header row
        writer.writerow(label_list)

        if "hours_on" in field_list and (not start_period or not end_period):
            first_day_of_last_month, last_day_of_last_month = last_month_day_info()
            if not start_period:
                start_period = first_day_of_last_month
            if not end_period:
                end_period = last_day_of_last_month
        if "hours_on" in field_list:
            print(
                "Using time range {} to {} for hours_on "
                "calculation.".format(start_period, end_period)
            )

        # server rows
        for server in servers:
            row = server_to_row(server, field_list, start_period, end_period)
            if row:
                writer.writerow(row)

        file_.seek(0)
        self.csv = file_.read()

        if use_stdout:
            print(self.csv)


def server_to_row(server, fields, start_period, end_period):
    """Return a tuple of the server's values for the fields in `fields`"""

    values = []
    for field in fields:
        if field == "hours_on":
            svr_rsrc_usage = server.get_resource_history(start_period, end_period)
            if svr_rsrc_usage:
                values.append(svr_rsrc_usage["hrs_on"])
            else:
                # no resource history means the server didn't exist during that period. The
                # server should not be included in the report in this case
                return None
            continue
        elif field == "cluster":
            # add the cluster that is stored on the vmware-specific info on the
            # server
            try:
                cluster = server.vmwareserverinfo.cluster
            except VmwareServerInfo.DoesNotExist:
                pass
            else:
                if cluster:
                    values.append(cluster)
                    continue
            # if there is no vmwareserverinfo or no value for cluster, get the
            # cluster from the vmware_cluster CFV on the environment instead
            cluster = server.environment.vmware_cluster or ""
            values.append(cluster)
            continue
        elif field == "tags":
            tags_csv = ",".join([t.name for t in server.tags.all()])
            values.append('"{}"'.format(tags_csv))
            continue
        try:
            values.append(getattr(server, field, ""))
        except AttributeError:
            stderr.write("Error: No field named '{}' exists.\n".format(field))
            exit(1)

    # the customer doesn't want lots of trailing zeroes for the significant
    # figures in Decimal values like mem_size, so we convert them to floats
    for i in range(len(values)):
        if isinstance(values[i], Decimal):
            values[i] = float(values[i])
    return tuple(values)


def write_report_to_file(report):
    """
    Save the contents of `file` to a file named `filename`

    Reports need their filename attribute defined.
    """
    with open(report.filename, "w+t") as new_file:
        new_file.write(report.csv)
    print("Exported to: {}".format(report.filename))


def email_report_to_group_admins(report):
    """
    Send the report as an attacment named `filename` to the administrators for
    the group named `group_name`.

    Reports need their filename and group_name attributes defined.
    """
    group = Group.objects.get(name=report.group_name)
    # This includes OOTB group_admins + resource_admins
    admins = group.get_profiles_for_permission(
        "group.change_attributes", include_global_roles=False
    )
    admins = (group.resource_admins.all() | group.user_admins.all()).distinct()
    # Exclude inactive/historical users
    addresses = [admin.user.email for admin in admins if admin.user.is_active]

    email_context = {"group": group}
    attachments = [(report.filename, report.csv, "text/csv")]

    email(
        recipients=addresses,
        slug="export-group-servers-report",
        context=email_context,
        attachments=attachments,
    )
    print("Emailed {} to {}".format(report.filename, ", ".join(addresses)))


def email_reports_to_addresses(reports, addresses):
    """
    Send an email CC'd to all of the `addresses` with all of the reports
    attached.
    """
    attachments = []
    for report in reports:
        # attachments are (filename, content, mimetype)
        attachments.append((report.filename, report.csv, "text/csv"))

    email(recipients=addresses, slug="export-servers-report", attachments=attachments)

    plurality = "report" if len(reports) == 1 else "reports"
    print("Emailed {} to {}".format(plurality, ", ".join(addresses)))


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "-f",
            "--fields",
            metavar="FIELDS",
            default="hostname",
            help="Export the values of the server field names listed "
            "in FIELDS (comma separated). Common FIELDS include: "
            "hostname,group,ip,disk_size,mem_size,cpu_cnt,os_family,"
            "tags,hours_on. "
            "  `hours_on` will be computed based on the previous "
            "  full month, unless -t or -n is specified. "
            "  `tags` will be a quoted CSV string of all tags. ",
        )
        parser.add_argument(
            "-g",
            "--groups",
            metavar="GROUPS",
            help="Only export data for servers belonging to any of the groups in GROUPS (comma separated)",
        )
        parser.add_argument(
            "-s",
            "--separate",
            action="store_true",
            help="Produce separate outputs for each group that is specified by --groups",
        )
        parser.add_argument(
            "-o",
            "--usestdout",
            action="store_true",
            default=False,
            dest="use_stdout",
            help="Send all CSV to stdout instead of file(s)",
        )
        parser.add_argument(
            "-p",
            "--prefix",
            metavar="PREFIX",
            default="exported-server-info",
            help="Add PREFIX to the beginning of all output filenames",
        )
        parser.add_argument(
            "-a",
            "--email-group-admins",
            action="store_true",
            help="Email each group-specific report to the group's admins "
            "(those with group.change_attributes permission). "
            "Implies --separate.",
        )
        parser.add_argument(
            "-e",
            "--email-to",
            metavar="ADDRESSES",
            help="Attach each report to an email and send it CC'd to the addresses in ADDRESSES (comma separated)",
        )
        parser.add_argument(
            "-t",
            "--startdate",
            metavar="STARTDATE",
            help="If the 'hours_on' field is specified, startdate and "
            "enddate will bound the hours the server was on. Should"
            "be specified in the format YYYY-MM-DD.",
        )
        parser.add_argument(
            "-n",
            "--enddate",
            metavar="ENDDATE",
            help="If the 'hours_on' field is specified, startdate and "
            "enddate will bound the hours the server was on.  Should "
            "be specified in the format YYYY-MM-DD.",
        )

    help = """Generate reports of servers and their field values in CSV format.

Examples:
  To write a file containing hostname and group name information for all
  servers:
    ./manage.py export_server_info -p report -f hostname,group

  To write separate files for the servers in group 'HR' and group 'IT':
    ./manage.py export_server_info -s -g HR,IT

  To email a report specific to each group to their respective admins, and then
  email all of those reports to user@example.com:
    ./manage.py export_server_info --email-group-admins --email-to=user@example.com"""

    def handle(self, *args, **options):
        # there is no `fields is not None` check because we set an optparse
        # default value for this option
        fields = options["fields"]
        field_list = fields.split(",")

        # A top-level queryset that all other group/whatever filtering will be
        # based on
        base_servers = Server.objects.all()
        if "hours_on" not in field_list:
            # In most cases, this report should not exclude historical servers. Only include them
            # if reporting on "hours_on", because a server may have existed during the time period,
            # even though it is historical now.
            base_servers = base_servers.exclude(status="HISTORICAL")

        group_list = []
        if options["groups"]:
            group_list = options["groups"].split(",")
            base_servers = base_servers.filter(group__name__in=group_list)
        else:
            # When does not specify any groups, but does request group
            # separation, we should automatically separate on all available
            # groups instead of doing no separation at all.
            group_list = [group.name for group in Group.objects.all()]

        startdate = None
        if options["startdate"]:
            startdate = mkDateTime(options["startdate"])

        enddate = None
        if options["enddate"]:
            enddate = mkDateTime(options["enddate"])
            # use the entire last day
            enddate = enddate.replace(hour=23, minute=59, second=59)

        address_list = []
        if options["email_to"]:
            address_list = options["email_to"].split(",")

        email_group_admins = options["email_group_admins"]
        # emailing group admins implies the separate behavior
        separate = options["separate"] or email_group_admins
        use_stdout = options["use_stdout"]
        prefix = options["prefix"]

        # Create the reports...

        all_reports = []  # list of every report generated

        if separate:
            for group_name in group_list:
                servers = base_servers.filter(group__name=group_name)
                if servers.count() == 0:
                    print(
                        "Did not create a report for the {} group because the group owns no servers".format(
                            group_name
                        )
                    )
                    continue
                report = Report(servers, field_list, use_stdout=use_stdout)
                report.filename = "{}_{}.csv".format(prefix, group_name)
                report.group_name = group_name
                all_reports.append(report)

        else:
            report = Report(
                base_servers, field_list, startdate, enddate, use_stdout=use_stdout
            )
            report.filename = "{}.csv".format(prefix)
            all_reports.append(report)

        # Deliver the reports...
        # It's useful to do the delivery as a separate step in case an error
        # happens in the middle of report creation so that errors during report
        # creation are less likely to cause delivery of some but not all
        # reports

        if address_list:
            email_reports_to_addresses(all_reports, address_list)

        if email_group_admins:
            for report in all_reports:
                email_report_to_group_admins(report)

        if not (address_list or email_group_admins or use_stdout):
            for report in all_reports:
                write_report_to_file(report)
