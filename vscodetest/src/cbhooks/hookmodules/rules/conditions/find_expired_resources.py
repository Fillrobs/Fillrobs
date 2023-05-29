#!/usr/bin/env python

"""
Looks for an Expiration Date parameter value on all non-historical deployed
resources and passes along a list of IDs for all the ones where the Expiration
Date has passed to the then actions so they can do something with them
"""
from __future__ import print_function

from datetime import datetime

from common.methods import set_progress
from resources.models import Resource

if __name__ == "__main__":
    import django

    django.setup()


def check(job, logger):
    now = datetime.utcnow()
    expired_resources = []

    possible_resources = Resource.objects.filter(
        attributes__field__name="expiration_date"
    ).exclude(lifecycle="HISTORICAL")
    for resource in possible_resources:
        val = resource.get_cfv_for_custom_field("expiration_date").value
        if val is not None:
            set_progress("Checking expiration date of {}".format(resource))
            if isinstance(val, str):
                try:
                    val = datetime.strptime(val, "%m/%d/%Y")
                except TypeError:
                    set_progress(
                        "Skipping {} due to bogus expiration date "
                        "format".format(resource)
                    )
                    continue
            if val < now:
                set_progress("{} is past its expiration date".format(resource))
                expired_resources.append(resource.id)

    set_progress("Passing {} resource(s) to be expired.".format(len(expired_resources)))
    resources_dict = {"resource_ids": expired_resources} if expired_resources else {}
    return "SUCCESS", "", "", resources_dict


if __name__ == "__main__":
    print(check(None, None))
