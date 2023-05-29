"""
LEGACY: With the 9.0 release, IPAM orchestration is now provided directly on the IPAM detail page
and can be enabled and customized there.

A hook that will replace the server ip from 'dhcp' with the infoblox reserved
IP value when applicable.  Even if the ResourceHandler is capable of resolving
DHCP issued IPs, this hook makes sure it matches the IP infoblox expects to be
on the servers.
Part of the Infoblox integration sample hook set, called from the
pre_application hook point.
"""
from __future__ import print_function
import traceback
import sys


def run(job, logger=None):
    debug("Running hook {}. job.id={}".format(__name__, job.id), logger)
    try:
        for server in job.server_set.all():
            server.ip = server.infoblox_ip
            server.save()

    except:  # noqa: E722
        outmsg = "Aborting job because of a dhcp replacement hook error"
        tb = traceback.format_exception(*sys.exc_info())
        errmsg = "\n" + "\n".join(tb)
        return ("FAILURE", outmsg, errmsg)
    return "", "", ""


def debug(message, logger):
    if logger:
        logger.debug(message)
    else:
        print(message)
