"""
LEGACY: With the 9.0 release, IPAM orchestration is now provided directly on the IPAM detail page
and can be enabled and customized there.

A hook that appends the DNS domain to the hostname, and calls infoblox to allocate the server IP
Part of the Infoblox integration sample hook set, called from the pre_create_resource hook point.
"""
from __future__ import print_function
import traceback
import sys


def allocate_ip(job, infoblox, host_fqdn):
    w = infoblox.get_wrapper_api()
    ip = None
    last_exception = None
    for net in w.networks():
        try:
            w.add_host_record(host_fqdn, "func:nextavailableip:%s" % net["_ref"])
            host_records = w.get_host_records(host_fqdn)

            if len(host_records) == 1:
                host_record = host_records[0]
                host_ipv4addrs = host_record["ipv4addrs"]
                if len(host_ipv4addrs) == 1:
                    ip = host_ipv4addrs[0]["ipv4addr"]
                    break

        except Exception as e:
            last_exception = e

    if last_exception:
        raise last_exception

    # Also register this host with other DNS views, e.g.:
    #
    # if ip:
    #     job.set_progress("New IP address is '%s'" % ip)
    #     w.add_host_record(host_fqdn, ip, view="{view-name}")
    # else:
    #     raise Exception("No IP allocated for '%s'" % (host_fqdn))

    return ip


def run(job, logger=None):
    debug("Running hook '{}'. job.id='{}'".format(__name__, job.id), logger)
    try:
        from ipam.models import IPAM

        infoblox = IPAM.objects.first()
        if not infoblox:
            return "FAILURE", "", "Missing required Infoblox connector"
        for server in job.server_set.all():

            fqdn = "{}.{}".format(server.hostname, server.dns_domain)

            msg = ("Adding domain to hostname: {} -> {}").format(server.hostname, fqdn)
            job.set_progress(msg)

            server.host_fqdn = fqdn

            # call infoblox to allocate the ip_address
            job.set_progress("Calling infoblox to allocate server IP")
            server.infoblox_ip = allocate_ip(job, infoblox, fqdn)

            server.save()
    except:  # noqa: E722
        outmsg = "Aborting job because of a pre_create_resource hook error"
        tb = traceback.format_exception(*sys.exc_info())
        errmsg = "\n" + "\n".join(tb)
        return ("FAILURE", outmsg, errmsg)
    return "", "", ""


def debug(message, logger):
    if logger:
        logger.debug(message)
    else:
        print(message)
