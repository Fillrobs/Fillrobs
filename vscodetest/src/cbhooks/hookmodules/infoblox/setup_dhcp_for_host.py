"""
LEGACY: With the 9.0 release, IPAM orchestration is now provided directly on the IPAM detail page
and can be enabled and customized there.

A hook that makes sure a host is registered in infoblox, so it receives a
(pre-selected) IP when requesting a DHCP address.
Part of the Infoblox integration sample hook set, called from the pre_networkconfig hook point
"""
from __future__ import print_function
import traceback
import sys


def setup_dhcp_for_host(infoblox, host_fqdn, mac_address):
    w = infoblox.get_wrapper_api()
    w.setup_dhcp_for_host(host_fqdn, mac_address)


def restart_dhcp_service(infoblox):
    w = infoblox.get_wrapper_api()
    w.restart_dhcp_service()


def run(job, logger=None):
    debug("Running hook {}. job.id={}".format(__name__, job.id), logger)
    try:
        from ipam.models import IPAM

        infoblox = IPAM.objects.first()
        if not infoblox:
            return "FAILURE", "", "Missing required Infoblox connector"
        for server in job.server_set.all():
            job.set_progress(
                "Calling infoblox to setup dhcp for host {}".format(server.host_fqdn)
            )

            setup_dhcp_for_host(infoblox, server.host_fqdn, server.mac)

        # after registering all servers restart the services so the
        # registrations are imediatelly available
        restart_dhcp_service(infoblox)

    except:  # noqa: E722
        outmsg = "Aborting pre_networkconfig job because of a hook error"
        tb = traceback.format_exception(*sys.exc_info())
        errmsg = "\n" + "\n".join(tb)
        return ("FAILURE", outmsg, errmsg)
    return "", "", ""


def debug(message, logger):
    if logger:
        logger.debug(message)
    else:
        print(message)
