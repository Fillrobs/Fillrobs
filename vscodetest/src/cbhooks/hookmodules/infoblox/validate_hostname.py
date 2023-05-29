"""
LEGACY: With the 9.0 release, IPAM orchestration is now provided directly on the IPAM detail page
and can be enabled and customized there.

A hook that makes sure a hostname is not already registered in infoblox, as a pre-create validation
step.
Part of the Infoblox integration sample hook set, called from the validate_hostname hook point
"""
from __future__ import print_function


def is_hostname_in_use(infoblox, host_fqdn):
    w = infoblox.get_wrapper_api()
    records = w.get_host_records(host_fqdn)
    return len(records) > 0


def run(job, logger=None):
    debug("Running hook {}. job.id={}".format(__name__, job.id), logger)

    from ipam.models import IPAM

    infoblox = IPAM.objects.first()
    if not infoblox:
        return "FAILURE", "", "Missing required Infoblox connector"
    server = job.server_set.first()  # provision job acts on a single server
    host_fqdn = "{}.{}".format(server.hostname, server.dns_domain)
    job.set_progress(
        "Checking if hostname '{}' is already in Infoblox".format(host_fqdn)
    )

    if is_hostname_in_use(infoblox, host_fqdn):
        return "FAILURE", "", "Found host record with hostname '{}'".format(host_fqdn)

    return "", "", ""


def debug(message, logger):
    if logger:
        logger.debug(message)
    else:
        print(message)
