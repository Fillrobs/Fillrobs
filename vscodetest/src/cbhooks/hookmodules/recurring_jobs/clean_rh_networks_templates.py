#!/usr/bin/env python

"""
Checks CB networks and templates for all applicable RHs against the current networks and
templates in the resource technology itself, in order to clean up any networks
or templates in CB that are no longer valid and make sure that users don't
attempt to use any that are out of sync with the resource technology.
"""
from __future__ import print_function

if __name__ == "__main__":
    import django

    django.setup()

from common.methods import set_progress
from resourcehandlers.models import ResourceHandler


def run(job, logger=None, **kwargs):
    status = "SUCCESS"
    rhs = ResourceHandler.objects.all()
    rh_cnt = rhs.count()
    msg = "Found {} resource handlers to check".format(rh_cnt)
    set_progress(msg, tasks_done=0, total_tasks=rh_cnt)
    for rh in rhs:
        rh = rh.cast()
        set_progress("Cleaning networks in '{}'.".format(rh))
        try:
            clean_networks(rh)
        except Exception as err:
            msg = "Cleaning networks in '{}' failed.".format(rh)
            logger.exception(msg)
            set_progress("{}\n{}".format(msg, err))
            status = "FAILURE"

        set_progress("Cleaning templates in '{}'.".format(rh))
        try:
            clean_templates(rh)
        except Exception as err:
            msg = "Cleaning templates in '{}' failed.".format(rh)
            logger.exception(msg)
            set_progress("{}\n{}".format(msg, err))
            status = "FAILURE"

        set_progress(increment_tasks=1)
    return status, "", ""


def clean_networks(rh):
    # The discover_networks method works for all RHs, simply returning empty
    # lists if the RH doesn't support networks
    _, _, only_in_cb = rh.discover_networks()
    # Remove networks that are missing from the RH
    set_progress("Removing {} networks from '{}'.".format(len(only_in_cb), rh))
    for network in only_in_cb:
        network.delete()


def clean_templates(rh):
    if rh.can_import_templates is False:
        set_progress("Skipping RH '{}', it can't discover templates.".format(rh))
        return

    # If this RH requires a region to discover templates (currently only AWS)
    # then iterate over its regions
    only_in_cb = []
    if rh.discover_templates_requires_region is True:
        for region in rh.current_regions():
            _, _, region_only_in_cb = rh.discover_templates(region_name=region)
            # Make sure we don't count a template as missing just because it's
            # for a different region
            for osba in region_only_in_cb:
                if osba.region == region:
                    only_in_cb.add(osba)
    else:
        _, _, only_in_cb = rh.discover_templates()

    # Remove templates that are missing from the RH
    set_progress("Removing {} templates from '{}'.".format(len(only_in_cb), rh))
    for osba in only_in_cb:
        rh.delete_osbuild_attribute(osba)


if __name__ == "__main__":
    from utilities.logger import ThreadLogger

    logger = ThreadLogger(__name__)
    print(run(None, logger))
