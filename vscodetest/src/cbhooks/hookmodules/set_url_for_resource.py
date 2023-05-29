#!/usr/bin/env python

"""
Takes the IP of a single server in a resource order and sets that as the value
for a Website URL parameter on the resource, which will then show up as an
attribute on that deployed resource.
"""

from infrastructure.models import CustomField
from orders.models import CustomFieldValue


def run(job, logger=None, **kwargs):
    resource = job.resource_set.first()
    server = resource.server_set.first()

    cf, _ = CustomField.objects.get_or_create(
        name="website_url",
        defaults={
            "label": "Website URL",
            "description": "The URL for the website created by a resource",
            "type": "URL",
        },
    )
    cf.show_as_attribute = True
    cf.save()

    url = "http://{}/".format(server.ip)
    cfv, _ = CustomFieldValue.objects.get_or_create(field=cf, value=url)
    resource.attributes.add(cfv)

    return "", "", ""
