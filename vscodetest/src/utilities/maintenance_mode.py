#!/usr/bin/env python
from __future__ import unicode_literals

from __future__ import print_function
import errno
import datetime
import os
import shutil
import sys

from django.template import Template, Context
from django.conf import settings

curdir = os.path.abspath(os.path.dirname(__file__))
cloudbolt_rootdir = os.path.dirname(curdir)
sys.path.insert(0, cloudbolt_rootdir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

if __name__ == "__main__":
    import django

    django.setup()

if not settings.configured:
    settings.configure()

from settings import MAINTENANCE_MODE_FILE


def render_to_file(template_filepath, dst_filepath, context):
    template_contents = open(template_filepath, "r").read()
    t = Template(template_contents)
    c = Context(context)
    rendered_content = t.render(c)
    open(dst_filepath, "w").write(rendered_content)


def silent_remove(filename):
    # Taken from http://stackoverflow.com/questions/10840533/most-pythonic-way-to-delete-a-file-which-may-not-exist
    try:
        os.remove(filename)
    except OSError as e:
        if e.errno != errno.ENOENT:  # errno.ENOENT = no such file or directory
            raise  # re-raise exception if a different error occured


def activate_maintenance_mode(page_context={}):
    shutil.copy("/var/www/html/maintenance_mode_htaccess", "/var/www/html/.htaccess")
    render_to_file(
        "/var/www/html/maintenance_template.html",
        "/var/www/html/maintenance.html",
        page_context,
    )
    MAINTENANCE_MODE_FILE_file = open(MAINTENANCE_MODE_FILE, "w")
    MAINTENANCE_MODE_FILE_file.write(
        "Maintenance mode began {}. To exit maintenance mode, "
        "run '/opt/cloudbolt/utilities/maintenance_mode.py off'.".format(
            datetime.datetime.now()
        )
    )
    MAINTENANCE_MODE_FILE_file.close()


def deactivate_maintenance_mode():
    silent_remove("/var/www/html/.htaccess")
    silent_remove(MAINTENANCE_MODE_FILE)
    # Remove the maintenance HTML page itself to avoid people hitting it and thinking that CB is
    # still under maintenance.
    page_context = {
        "title": "Maintenance Complete",
        "body": "CloudBolt is no longer in maintenance mode, click below to return to the product.",
    }
    render_to_file(
        "/var/www/html/maintenance_template.html",
        "/var/www/html/maintenance.html",
        page_context,
    )


def is_in_maintenance_mode():
    return os.path.isfile(MAINTENANCE_MODE_FILE)


def parse_cmdline():
    import argparse

    parser = argparse.ArgumentParser(
        description=(
            "Enables and disables maintenance mode for CloudBolt. When enabled, all "
            "users of the web UI will be redirected to a maintenance page with the title & body "
            "specified (sensible defaults will "
            "be used if these arguments are not specified). When maintenance mode is on, "
            "the CloudBolt job engine will continue with jobs that are already running, but will not "
            "pick up new pending jobs, and will not restart once it has exited. "
            "This only affects the CB server it is run on; if you have multiple CB servers, "
            "and want to put them all in maintenance mode, this will need to be run on each. The "
            "CloudBolt upgrader will automatically activate maintenance mode (if it is not already "
            "activated)."
        )
    )
    parser.add_argument(
        "action", choices=["on", "off", "status"], help="specifies what action to take"
    )
    # required options
    parser.add_argument(
        "--title",
        "-t",
        help="this is used as the title of the webpage and the main heading text on the page",
        default=None,
        required=False,
    )
    parser.add_argument(
        "--body", "-b", help="body of the page.", default=None, required=False
    )
    kwargs = {}
    args = parser.parse_args()
    if args.title:
        kwargs["title"] = args.title
    if args.body:
        kwargs["body"] = args.body
    return args.action, kwargs


if __name__ == "__main__":
    action, kwargs = parse_cmdline()
    if action == "on":
        activate_maintenance_mode(page_context=kwargs)
        print("Maintenance mode enabled.")
    elif action == "off":
        deactivate_maintenance_mode()
        print("Maintenance mode disabled.")
    elif action == "status":
        if is_in_maintenance_mode():
            print("Maintenance mode on.")
        else:
            print("Maintenance mode off.")
    else:
        raise Exception(
            "Unknown action ('{}') specified, action should be 'on', 'off', or 'status'.".format(
                action
            )
        )
