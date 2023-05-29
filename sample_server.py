"""
This plug-in can be used in various contexts to reboot the server(s) available
to it, or some subset thereof. For example, you can reboot a single server after
it is provisioned by adding this at the Post-Network Configuration trigger point
for orchestration actions.
"""

import time
from common.methods import set_progress
from infrastructure.models import Server


def generate_options_for_myservers(**kwargs):
    options = []
    initial = ("", "------")
    options.append(initial)
    servers = Server.objects.filter(status='ACTIVE')
    for server in servers:
        svr_id = server.id
        svr_name = server.hostname
        options.append((svr_id, svr_name))
    return options    


def run(job, logger=None, **kwargs):
    svr_ids = '{{ myservers }}'
    if isinstance(svr_ids, str):
        svr_ids = [svr_ids]
    # Django query - filter is powerful     
    servers = Server.objects.filter(id__in=svr_ids)
    
    # In some cases, such as a provision job, this will only contain 1 server.
    # To only reboot a subset of the servers, you can filter this group. For
    # example, to only reboot those whose hostname starts with CB you can do:
    # servers = [svr for svr in servers if svr.hostname.startswith('CB')]

    profile = None
    if job:
        profile = job.owner

    failed_servers = []

    for server in servers:
        """
        if server.can_reboot():
            set_progress("Rebooting server '{}'".format(server.hostname))
            success = server.reboot(profile)
            if not success:
                failed_servers.append(server.hostname)
            # Wait 20s for the reboot to begin so the call to wait_for_os_readiness
            # does not return immediately because the server hasn't started
            # rebooting yet
            time.sleep(20)
            server.wait_for_os_readiness()
        else:
            set_progress(
                "Skipping reboot of server '{}' because not supported".format(
                    server.hostname
                )
            )
        """
        set_progress(f"Handling Server : {server}")

    if failed_servers:
        failed_list = ", ".join(failed_servers)
        return "FAILURE", "Rebooting failed on {}".format(failed_list), ""

    return "", "", ""