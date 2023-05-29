"""
LEGACY: With the 9.0 release, IPAM orchestration is now provided directly on the IPAM detail page
and can be enabled and customized there.

A hook that frees up IPs back to the reservation pool in infoblox when servers are deleted.
Part of the Infoblox integration sample hook set, called from the post_decom hook point.
"""
from __future__ import print_function

import traceback
import sys


def delete_host(infoblox, host_fqdn):
    w = infoblox.get_wrapper_api()

    w.delete_host_record(host_fqdn)

    # Delete record from other DNS views as needed e.g.:
    #
    #  w.delete_host_record(host_fqdn, view="{view-name}")


def run(job, logger=None):
    debug("Running hook {}. job.id={}".format(__name__, job.id), logger)
    try:
        from ipam.models import IPAM

        infoblox = IPAM.objects.first()
        if not infoblox:
            return "FAILURE", "", "Missing required Infoblox connector"
        for server in job.server_set.all():
            if server.resource_handler.type_slug == "aws":
                return "", "", ""

            # call infoblox to delete host
            job.set_progress(
                "Calling infoblox to delete host {}".format(server.host_fqdn)
            )

            delete_host(infoblox, server.host_fqdn)

    except:  # noqa: E722
        outmsg = "Aborting job because of a post_delete hook error"
        tb = traceback.format_exception(*sys.exc_info())
        errmsg = "\n" + "\n".join(tb)
        return ("FAILURE", outmsg, errmsg)
    return "", "", ""


def debug(message, logger):
    if logger:
        logger.debug(message)
    else:
        print(message)
