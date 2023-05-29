#!/usr/bin/env python

"""
A hook that prefixes the hostname of every with the first three letters of its
group's name.
"""
from __future__ import print_function

import traceback
import sys

if __name__ == "__main__":
    import django

    django.setup()

from django.utils.html import format_html
from jobs.models import Job
from orders.models import ProvisionServerOrderItem


def create_dr_instance(job, server, oi, logger=None):
    """
    TODO: move this into a factory class, also very similar code in servicecatalog/models.py
    """
    newoi = ProvisionServerOrderItem.objects.create(
        quantity=oi.quantity, os_build=oi.os_build
    )
    newoi.applications.set(oi.applications.all())
    newoi.custom_field_values.set(oi.custom_field_values.all())
    newoi.preconfiguration_values.set(oi.preconfiguration_values.all())
    newoi.hostname = str(oi.hostname) + "-dr"
    newoi.order = oi.order
    newoi.environment = oi.environment
    newoi.save()
    newjob = Job.objects.create(job_parameters=newoi, type=job.type, owner=job.owner)
    joblink = format_html("<a href={}>job #{}</a>", job.get_absolute_url(), job.id)
    msg = format_html("Created {} to build a DR VM.", joblink)
    job.set_progress(msg)
    return newjob


def run(job, logger=None):
    debug("Running hook {}. job.id={}".format(__name__, job.id), logger)

    oi = job.order_item
    if False and not oi.environment.name.startswith("Prod"):
        msg = "Not deploying to a production environment, will not create a DR VM."
        job.set_progress(msg)
        return "", "", ""

    try:
        for server in job.server_set.all():
            if server.hostname.endswith("-dr"):
                # this is already a DR instance
                continue

            create_dr_instance(job, server, oi, logger)

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


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.stderr.write("usage: %s <Job id>\n" % (sys.argv[0]))
        sys.exit(2)
    job_id = sys.argv[1]
    job = Job.objects.get(pk=job_id)
    status, msg, err = run(job)
    print("status, msg, err = {} {} {}".format(status, msg, err))
