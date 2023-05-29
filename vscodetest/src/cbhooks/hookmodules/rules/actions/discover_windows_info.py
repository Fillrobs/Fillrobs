#!/bin/env python
from __future__ import print_function
import traceback
import sys
import json

from jobs.models import Job
from jobengine.jobmodules.syncvmsjob import ServerUpdater
from externalcontent.models import OSFamily
from resourcehandlers.ipmi.models import IPMIResourceHandler


if __name__ == "__main__":
    import django

    django.setup()


def debug(message, logger):
    if logger:
        logger.debug(message)
    else:
        print(message)


def run(job, logger=None):
    debug("Running hook {}. job.id={}".format(__name__, job.id), logger)

    ps_cmd_services = 'Get-WmiObject -Class "win32_service" | ConvertTo-Json'
    ps_cmd_cron = 'get-WmiObject -Class "Win32_ScheduledJob" | ConvertTo-Json'
    ps_cmd_users = 'Get-WmiObject -Class Win32_UserAccount -filter "LocalAccount = True" | ConvertTo-Json'
    ps_cmd_ldisk = "Get-WmiObject -Class Win32_LogicalDisk | ConvertTo-Json"
    ps_cmd_pdisk = "Get-WmiObject -Class Win32_DiskDrive | ConvertTo-Json"
    ps_cmd_part = "Get-WmiObject -Class Win32_DiskPartition | ConvertTo-Json"
    ps_cmd_server_info = "Get-WmiObject -Class Win32_ComputerSystem | ConvertTo-Json"

    # Use the IPMI resource handler for discovered physical servers.
    rh = IPMIResourceHandler.objects.first()

    # The rule might pass multiple servers.
    for server in job.server_set.all():
        try:
            # Gather and store OS info in os-specific parameters.
            server.os_services = server.execute_script(script_contents=ps_cmd_services)
            server.os_cron = server.execute_script(script_contents=ps_cmd_cron)
            server.os_users = server.execute_script(script_contents=ps_cmd_users)
            server.os_disks_logical = server.execute_script(
                script_contents=ps_cmd_ldisk
            )
            server.os_disks_physical = server.execute_script(
                script_contents=ps_cmd_pdisk
            )
            server.os_partitions = server.execute_script(script_contents=ps_cmd_part)

            # Use vm_dict structure to update the Server record details.
            os_server_info = server.execute_script(script_contents=ps_cmd_server_info)
            os_server_info = json.loads(os_server_info, strict=False)
            vm_dict = {}
            vm_dict["os_family"] = OSFamily.objects.get(name="Windows")
            vm_dict["power_status"] = "POWERON"
            vm_dict["hostname"] = os_server_info.get("Name")
            updater = ServerUpdater(server, vm_dict, created=False, rh=rh)
            updater.update()
            server.save()

        except:  # noqa: E722
            tb = traceback.format_exception(*sys.exc_info())
            msg = "Error when saving OS services for {} [{}]: {}"
            msg = msg.format(server.hostname, server.id, tb)
            debug(msg, logger)
    return "SUCCESS", "", ""


if __name__ == "__main__":
    # Useful for testing purposes
    print(run(job=Job.objects.get(id=sys.argv[1]),))
