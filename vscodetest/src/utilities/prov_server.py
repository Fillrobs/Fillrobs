#!/usr/bin/env python

"""
This is a script that will create a server using a CloudBolt instance. I
expect to be run from src/initialize/
"""

from __future__ import unicode_literals, print_function
import getopt
import os
import sys
import time


def die(errcode=5):
    sys.exit(errcode)


def spew(msg, error=False):
    " Logging function. "
    if error:
        msg = "[[ERROR]]>%s" % (msg)
    print(msg)


def usage(msg=""):
    spew(
        msg="""
Arguments:
    -u or --user=
      username to own the VM

    -p or --project=
      project to create the VM in

    -s or --environment=
      environment to create the VM in

    -o or --os=
      os to provision the VM with

    -v or --value=
      --value or -v arguments need to be : separated in the format of:

        --value=value_type:name:value

      where:
        - value_type is one of:
        * pcv (for preconfiguration value)
        * cfv (for custom field value)
        - name is the name of the field
        - value is the value to associate with the field

    -a or --app=
      application to add to the VM

    -q or --quantity=
      number of VM's to provision

    -h or --help
      this message

Example (that works with the default CloudBolt data):
%s -u super -s "Rockville Dev Lab" -p "Bonds" -q 1 -o "CentOS 6.3 Template" -v pcv:vm_size:small

%s
"""
        % (sys.argv[0], msg)
    )


mydir = os.path.dirname(sys.argv[0])
if mydir == "." or mydir == "":
    mydir = os.getcwd()

pathadds = [".", "../", "../../", mydir]
for x in pathadds:
    sys.path.insert(0, x)

os.chdir("%s/.." % mydir)

argv = sys.argv[1:]
shortOptions = "hu:p:s:o:v:a:q:"
longOptions = [
    "user=",
    "project=",
    "environment=",
    "os=",
    "value=",
    "app=",
    "quantity=",
    "help",
]

try:
    opts, rest = getopt.getopt(argv, shortOptions, longOptions)
except getopt.error as errorStr:
    spew(msg="%s" % (errorStr), error=True)
    usage()
    sys.exit(2)

user = None
project = None
environment = None
os_build = None
quantity = 1
custom_field_values = {}
preconfig_values = {}
apps = []

for opt, arg in opts:
    if opt in ("-h", "--help"):
        usage()
        sys.exit(0)
    if opt in ("--user", "-u"):
        user = arg
    if opt in ("--project", "-p"):
        project = arg
    if opt in ("--environment", "-s"):
        environment = arg
    if opt in ("--os", "-o"):
        os_build = arg
    if opt in ("--value", "-v"):
        fmsg = """
--value or -v arguments needs to be : separated in the format of:

  --value=value_type:name:value

  where:
    - value_type is one of:
    * pcv (for preconfiguration value)
    * cfv (for custom field value)
    - name is the name of the field
    - value is the value to associate with the field

    You supplied: %s
""" % (
            arg
        )

        try:
            val_type, val_key, val_value = arg.split(":")
            # print val_type, val_key, val_value
        except Exception:
            spew(msg=fmsg, error=True)
            die()
        if val_type == "pcv":
            preconfig_values[val_key] = val_value
        elif val_type == "cfv":
            custom_field_values[val_key] = val_value
        else:
            spew(msg=fmsg, error=True)
            die()
    if opt in ("--app", "-a"):
        apps.append(arg)
    if opt in ("--quantity", "-q"):
        try:
            quantity = int(arg)
        except Exception:
            fmsg = """
--quantity or -q arguments must be an integer!

    You supplied: %s
""" % (
                arg
            )
            spew(msg=fmsg, error=True)
            die()


if not user or not project or not environment or not os_build:
    usage("You supplied: %s , %s" % (opts, rest))
    die()

spew(msg="User: %s" % (user))
spew(msg="Project: %s" % (project))
spew(msg="Environment: %s" % (environment))
spew(msg="OS: %s" % (os_build))
spew(msg="Preconfiguration Values: %s" % (preconfig_values))
spew(msg="Custom Field Values: %s" % (custom_field_values))
spew(msg="Applications: %s" % (apps))
spew(msg="Quantity: %s" % (quantity))

if "DJANGO_SETTINGS_MODULE" not in os.environ:
    os.environ["DJANGO_SETTINGS_MODULE"] = "settings"

if __name__ == "__main__":
    import django

    django.setup()

# TODO: need to find a more intelligent way to locate c2_wrapper
from c2_wrapper import (
    create_provision_order,
    approve_order_and_start,
    wait_for_jobs,
    Job,
)

# create the provision order
retcode, prov_order_obj = create_provision_order(
    user=user,
    project=project,
    environment=environment,
    os_build=os_build,
    preconfig_values=preconfig_values,
    custom_field_values=custom_field_values,
    apps=apps,
    quantity=quantity,
)

# approve and run the provision order
if prov_order_obj:
    spew(msg="Running provisioning for %s servers" % (quantity))
    prov_job_objects = approve_order_and_start(prov_order_obj.id)
    wait_for_jobs(prov_job_objects)
else:
    spew(msg="Failure occurred while creating provision order!", error=True)
    die()

# collect success/fail servers from each job
prov_failures = []
prov_success_server_objects = []

for job_obj in prov_job_objects:
    # get an up-to-date instance of the job object
    job_obj = Job.objects.get(pk=job_obj.id)
    if job_obj.status == "SUCCESS":
        servers = job_obj.server_set.all()
        prov_success_server_objects += servers
    else:
        dt = time.ctime(time.time())
        msg = "%s: Job %s ended with status %s.  Output:\n%s\nErrors:\n%s\n" % (
            dt,
            job_obj.id,
            job_obj.status,
            job_obj.output,
            job_obj.errors,
        )
        prov_failures.append(msg)

if prov_success_server_objects:
    spew(msg="These are the successful servers that have been provisioned:")
    for serv in prov_success_server_objects:
        spew(msg="NEW_SERVER:%s:%s" % (serv.id, serv.ip))

if prov_failures:
    spew(prov_failures, error=True)
    die()
