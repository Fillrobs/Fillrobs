#!/usr/bin/env python
from __future__ import unicode_literals, print_function

# this is a script that will decom a server using a CloudBolt
# instance. I expect to be run from src/initialize/

import getopt
import os
import sys


def die(errcode=5):
    sys.exit(errcode)


def spew(msg, error=False):
    " Logging function. "
    if error:
        msg = "[[ERROR]]>%s" % (msg)
    print(msg)


def usage():
    print(
        """
Arguments:
  Specifying servers individually:

    -d or --id=
      CloudBolt id of the server to delete

    -n or --hostname=
      Name of the server to delete in CloudBolt

    -i or --ip=
      IP Address of the server to delete in CloudBolt

  Note 1: -d, -n, or -i can be specified multiple times
  Note 2: Any servers that don't match the environment and project of the
          first server specified will not be decom'd.

  Specifying all servers belonging to a specific environment and project:

    -s or --environment=
      Environment name to delete all servers from in CloudBolt

    -g or --group=
      Group name to delete all servers from in CloudBolt

  Note 1: Both --environment and --group must be specified
  Note 2: You can combine -n, -d, -i with --environment and --group

  Other:

    -h or --help
      this message

"""
    )


def find_servers(all_servers, srvattr, srvvalue, selected_servers=[]):
    """
    Filters all_servers for servers that have attributes that match srvvalue
    and adds them to selected_servers. Skips any servers that don't match
    the environment or group of the first server in selected_servers.
    """

    found_servers = [s for s in all_servers if getattr(s, srvattr) == srvvalue]
    if not found_servers:
        spew(msg="No servers found with %s == %s" % (srvattr, srvvalue))

    print(found_servers)

    for srv in found_servers:
        # no servers in selected_servers already, so just add it
        if not selected_servers:
            selected_servers.append(srv)
            spew(msg="Selected server %s for decom" % (srv))
            continue

        if srv in selected_servers:
            spew(msg="Server %s already selected!" % (srv))
            continue

        # if there are already servers in selected_servers
        # validate that this server has the same
        # environment and project as the first server
        if srv.environment != selected_servers[0].environment:
            spew(msg="Server %s environment (%s) does not match %s, skipping!") % (
                srv,
                srv.environment,
                selected_servers[0].environment,
            )
            continue

        if srv.group != selected_servers[0].group:
            spew(msg="Server %s group (%s) does not match %s, skipping!") % (
                srv,
                srv.group,
                selected_servers[0].group,
            )
            continue

        selected_servers.append(srv)
        spew(msg="Selected server %s for decom" % (srv))

    return selected_servers


mydir = os.path.dirname(sys.argv[0])
if mydir == "." or mydir == "":
    mydir = os.getcwd()

pathadds = [".", "../", "../../", mydir]
for x in pathadds:
    sys.path.insert(0, x)

os.chdir("%s/.." % mydir)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

if __name__ == "__main__":
    import django

    django.setup()

# TODO: need to find a more intelligent way to locate c2_wrapper
from c2_wrapper import create_decom_order, approve_order_and_start, wait_for_jobs, Job
from infrastructure.models import Server

argv = sys.argv[1:]
shortOptions = "hd:n:i:q:s:g:"
longOptions = ["id=", "hostname=", "ip=", "environment=", "group=", "help"]

try:
    opts, rest = getopt.getopt(argv, shortOptions, longOptions)
except getopt.error as errorStr:
    print("Error: %s" % errorStr)
    usage()
    sys.exit(2)

all_servers = Server.objects.filter(status="ACTIVE")

if not all_servers:
    spew(msg="No active servers found in CloudBolt!", error=True)
    die()

selected_servers = []
environment = None
group = None

for opt, arg in opts:

    if opt in ("-h", "--help"):
        usage()
        sys.exit(0)

    if opt in ("-d", "--id"):
        selected_servers.extend(
            find_servers(
                all_servers=all_servers,
                selected_servers=selected_servers,
                srvattr="id",
                srvvalue=int(arg),
            )
        )

    if opt in ("-n", "--hostname"):
        selected_servers.extend(
            find_servers(
                all_servers=all_servers,
                selected_servers=selected_servers,
                srvattr="hostname",
                srvvalue=arg,
            )
        )

    if opt in ("--ip", "-i"):
        selected_servers.extend(
            find_servers(
                all_servers=all_servers,
                selected_servers=selected_servers,
                srvattr="ipaddress",
                srvvalue=arg,
            )
        )

    if opt in ("--environment", "-s"):
        environment = arg

    if opt in ("--group", "-g"):
        group = arg

if environment and not group:
    spew(msg="You must specify --group with --environment", error=True)
    die()

if group and not environment:
    spew(msg="You must specify --environment with --group", error=True)
    die()

if environment and group:
    found_servers = Server.objects.filter(
        environment__name=environment, group__name=group, status="ACTIVE"
    )
    if found_servers:
        if selected_servers:
            if found_servers[0].environment != selected_servers[0].environment:
                spew(msg="Server %s environment (%s) does not match %s, skipping!") % (
                    found_servers[0],
                    found_servers[0].environment,
                    selected_servers[0].environment,
                )
            elif found_servers[0].group != selected_servers[0].group:
                spew(msg="Server %s group (%s) does not match %s, skipping!") % (
                    found_servers[0],
                    found_servers[0].group,
                    selected_servers[0].group,
                )
            else:
                for srv in found_servers:
                    if srv in selected_servers:
                        spew(msg="Server %s already selected!" % (srv))
                    else:
                        selected_servers.append(srv)
                        spew(msg="Selected server %s for decom" % (srv))
        else:
            for srv in found_servers:
                if srv in selected_servers:
                    spew(msg="Server %s already selected!" % (srv))
                else:
                    selected_servers.append(srv)
                    spew(msg="Selected server %s for decom" % (srv))
    else:
        spew(
            msg="No servers found with environment %s and group %s"
            % (environment, group)
        )

if not selected_servers:
    spew(msg="You need to specify a server to delete!", error=True)
    die()

# uniqify
selected_servers = list(set(selected_servers))

# create the decom order
retcode, decom_order_obj = create_decom_order(selected_servers)

# approve and run the decom order
if decom_order_obj:
    spew(
        msg="Running deletion for %s server(s) (%s)"
        % (len(selected_servers), selected_servers)
    )
    decom_job_objects = approve_order_and_start(decom_order_obj.id)
    wait_for_jobs(decom_job_objects)
else:
    spew(msg="Failure occurred while creating deletion order!", error=True)
    die()

for job_obj in decom_job_objects:
    # get an up-to-date instance of the job object
    job_obj = Job.objects.get(pk=job_obj.id)
    if job_obj.status != "SUCCESS":
        spew(msg="%s decommission job failed to run!" % (job_obj), error=True)
        die()
