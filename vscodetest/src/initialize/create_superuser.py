#!/usr/bin/env python
from __future__ import print_function, unicode_literals
import optparse
import os
import sys


# script to create CloudBolt admin users
__version__ = "0.0.9"

mydir = os.path.dirname(sys.argv[0])

pathadds = ["../", "."]

sys.path.insert(0, mydir)
os.chdir(mydir + "/..")

for x in pathadds:
    sys.path.insert(0, x)

os.environ["DJANGO_SETTINGS_MODULE"] = "settings"

if __name__ == "__main__":
    import django

    django.setup()

# import these after Django is initialized
from c2_wrapper import (
    create_cbadmin,
    create_cloudbolt_group,
    grant_cloudbolt_group_priv,
    grant_super_admin,
)


def parseArgs(args):
    # setup and return parsed arguments
    global parser
    parser = optparse.OptionParser(
        description=__doc__,
        version=__version__,
        usage="%s -u USERNAME -p PASSWORD -f FIRSTNAME -l LASTNAME -e EMAIL"
        % (sys.argv[0]),
    )
    parser.add_option("-u", "--username", dest="username", action="store")
    parser.add_option("-f", "--firstname", dest="firstname", action="store")
    parser.add_option("-l", "--lastname", dest="lastname", action="store")
    parser.add_option("-p", "--password", dest="password", action="store")
    parser.add_option("-e", "--email", dest="email", action="store")

    return parser.parse_args(args)


(options, args) = parseArgs(sys.argv)

optloop = ["username", "firstname", "lastname", "password", "email"]
for x in optloop:
    if not getattr(options, x):
        print("Must supply all the options as follows:")
        print(parser.usage)
        sys.exit(1)

super_user = create_cbadmin(
    username=options.username,
    first_name=options.firstname,
    last_name=options.lastname,
    password=options.password,
    email=options.email,
)
grant_super_admin(super_user)

# Create the Unassigned group (since this script may run before cb_minimal.py)
group_dict = {"name": "Unassigned", "type": "Organization", "parent": None}
group = create_cloudbolt_group(group_dict=group_dict)

# Give the new admin user all permissions to this group (except requestor):
group_privs = ["approver", "group_admin", "viewer", "resource_admin"]
group = grant_cloudbolt_group_priv("Unassigned", group_privs, super_user)
