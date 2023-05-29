#!/usr/bin/env python
import json  # noqa: F841, F401

from accounts.models import Group
from cbhooks.models import CloudBoltHook
from common.methods import set_progress
from externalcontent.models import OSFamily
from infrastructure.models import Server, Environment, ServerNetworkCard
from resourcehandlers.ipmi.models import IPMIResourceHandler
from utilities import events
from utilities.exceptions import CommandExecutionException

if __name__ == "__main__":
    import django

    django.setup()


def get_os_fam(os_fam_string):
    return OSFamily.objects.filter(name=os_fam_string).first()


def check_and_add_creds(svr, job, logger):
    """
    If a password was provided, attempt to run a script on the server to see if the provided
    creds are good. If so, store them.

    :return True if they worked, False if not.
    """
    parent_job = job.parent_job
    condition_args = parent_job.job_parameters.cast().arguments.get("context", {})
    password = condition_args.get("password", "")
    if not password:
        return

    username = condition_args.get("username", "")
    kwargs = {}
    if username:
        # only pass a runas_username if it's defined, otherwise let execute_script() use the default
        kwargs["runas_username"] = username

    set_progress("Testing credentials on {}".format(svr))
    try:
        # "echo" works nicely on both Windows & Linux
        svr.execute_script(
            script_contents='echo "Hello newly discovered world!"',
            runas_password=password,
            **kwargs,
        )
    except CommandExecutionException:
        set_progress(
            "Those credentials did not work, they will not be stored on this server."
        )
        logger.exception("Those creditials did not work.")
        return False
    else:
        set_progress("Those credentials worked, they will be stored on this server.")
        # This stores them in the proper custom field values on the server
        svr.username = username
        svr.password = password
        return True


def discover_server_info(svr, job, logger):
    """
    For each OS family in this server's OS family tree, look for CB plugins called "Discover
    <OS Family Name> ..." and run them.

    These plugins should execute remote scripts on the server and store info they find in
    whatever manner makes sense.

    This allows for multiple hooks to be run for each server, and different hooks for more &
    less specific OS families (ex. one may want to provide a CentOS discovery hook & a separate,
    more general Linux one).
    """
    current_os_fam = svr.os_family
    while current_os_fam:
        hooks = CloudBoltHook.objects.filter(
            name__startswith="Discover {} ".format(current_os_fam.name)
        )
        logger.debug(
            "Found {} info discovery hooks to run for {}.".format(
                hooks.count(), current_os_fam.name
            )
        )
        for hook in hooks:
            try:
                hook.run(job=job, show_tb_in_progress=False)
            except:  # noqa: E722
                msg = "Error raised when running discovery action {}. ".format(
                    hook.name
                )
                set_progress(msg + " See the job log for more info.")
                logger.exception(msg)

        current_os_fam = current_os_fam.parent


def run(job, logger, **kwargs):
    group = Group.objects.get(name="Unassigned")
    environment = Environment.objects.get(name="Unassigned")
    rh = IPMIResourceHandler.objects.first()
    params = job.job_parameters.cast().arguments
    errors = []

    for ip in list(params.keys()):
        set_progress("Creating server for IP {}".format(ip))
        os_family = get_os_fam(params[ip]["os_family"])
        hostname = params[ip].get("hostname", "")
        mac = params[ip].get("mac", "")
        svr = Server.objects.create(
            group=group,
            environment=environment,
            ip=ip,
            resource_handler=rh,
            os_family=os_family,
            hostname=hostname,
            mac=mac,
            power_status="POWERON",
        )
        svr.tags.add("physical")
        msg = "Server discovered during a network scan"
        events.add_server_event("ONBOARD", svr, msg, job=job)
        job.server_set.add(svr)
        ServerNetworkCard.objects.create(index=0, mac=mac, ip=ip, server=svr)
        can_login = check_and_add_creds(svr, job, logger)
        if can_login:
            discover_server_info(svr, job, logger)

    if errors:
        err_string = " \n".join(errors)
        return "FAILURE", "", err_string

    return "", "", ""
