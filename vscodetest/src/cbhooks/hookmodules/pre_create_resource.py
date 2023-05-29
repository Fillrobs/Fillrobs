"""
A hook that prefixes the hostname of every with the first three letters of its
group's name.
"""
from __future__ import print_function

import traceback
import sys


def run(job, logger=None):
    debug("Running hook {}. job.id={}".format(__name__, job.id), logger)
    try:
        for server in job.server_set.all():
            prefix = server.group.name[:3]

            old_hostname = server.hostname
            new_hostname = "{}-{}".format(prefix, server.hostname)

            msg = (
                "Prefixing hostname with first three letters of " "group name: {} -> {}"
            ).format(old_hostname, new_hostname)
            job.set_progress(msg)

            server.hostname = new_hostname
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
