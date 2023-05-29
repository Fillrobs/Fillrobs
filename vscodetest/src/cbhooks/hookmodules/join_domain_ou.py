#!/usr/local/bin/python

from __future__ import print_function
import sys
from common.methods import set_progress
import re

"""
Example Hook to join a Windows server to a particular OU of an AD domain.

Requires 4 parameters:

    1) domain - This is the AD domain you want the server to join. Ex:
    lab.iad.cloudboltsw.com

    2) ou - The ou you want the server to join. Ex:
    ou=cb_users,dc=lab,dc=iad,dc=cloudboltsw,dc=com

    3) domain_username - The username used to add the server to the domain. Ex:
    LAB_IAD\Administrator  # noqa:W605

    4) domain_password - The password used to add the server to the domain.

Additional parameters: In order to run the necessary script on the server,
CloudBolt must know the username and password with which to log into the
template. By default, CloudBolt uses the Administrator username. The password
can be set using either the 'Windows Server Password' or 'VMware Template Password'
parameters. If the username on the template is not Administrator, use the
'Server Username' parameter.

This hook will be especially useful as a post-provisioning hook.

Note: If the server is already in the specified domain (even if it is not in the
requested OU), the script will not change anything and will print a message
saying the server cannot be added to the domain again.

Note: The password provided will be temporarily stored in plain text in a PowerShell script
file on the system, but the file will be deleted when the task is complete.

Testing this hook: To speed up the developement cycle of testing this hook, it
can be run from the command line. Using a completed server provision job, run
`./join_domain_ou.py <job id>`. The job's originating order must have had the
above parameters already set.
"""


def run(job, logger):
    # If the job this is associated with fails, don't do anything
    if job.status == "FAILURE":
        return "", "", ""

    server = job.server_set.last()
    if not server.is_windows():
        msg = "Skipping joining domain for non-windows VM"
        return "", msg, ""
    if not server.resource_handler.cast().can_run_scripts_on_servers:
        logger.info("Skipping hook, cannot run scripts on guest")
        return "", "", ""

    set_progress("Joining OU in Domain based on parameters")

    domain = server.get_value_for_custom_field("domain")
    ou = server.get_value_for_custom_field("ou")
    username = server.get_value_for_custom_field("domain_username")
    password = server.get_value_for_custom_field("domain_password")

    fail_msg = "Parameter '{}' not set, cannot run hook"

    # confirm that all custom fields have been set
    if not domain:
        msg = fail_msg.format("domain")
        return "FAILURE", msg, ""
    elif not ou:
        msg = fail_msg.format("ou")
        return "FAILURE", msg, ""
    elif not username:
        msg = fail_msg.format("domain_username")
        return "FAILURE", msg, ""
    elif not password:
        msg = fail_msg.format("domain_password")
        return "FAILURE", msg, ""

    script = [
        "Add-Computer ",
        '-DomainName "{}" '.format(domain.strip()),
        '-OUPath "{}" '.format(ou.strip()),
        "-Credential ",
        "(",
        "New-Object ",
        "System.Management.Automation.PSCredential (",
        '"{}", '.format(username.strip()),
        '(ConvertTo-SecureString "{}" -AsPlainText -Force)'.format(password.strip()),
        ")) ",
    ]

    script = "".join(script)

    # For debugging. We'll eventually put this in the code base directly.
    username = server.get_credentials()["username"]
    msg = "Executing script on server using username '{}'".format(username)
    logger.info(msg)

    try:
        output = server.execute_script(script_contents=script)
        logger.info("Script returned output: {}".format(output))
    except RuntimeError as err:
        set_progress(str(err))
        # If the error is due to already being in the domain, it's OK
        errmsg = re.sub(r"\r", "", str(err))
        errmsg = re.sub(r"\n", "", errmsg)
        found = re.search(r"because it is already in that domain", errmsg)
        if not found:
            return "FAILURE", str(err), ""

    return "", "", ""


if __name__ == "__main__":
    from jobs.models import Job
    from utilities.logger import ThreadLogger

    logger = ThreadLogger(__name__)
    job_id = sys.argv[1]
    job = Job.objects.get(id=job_id)

    print(run(job, logger))
