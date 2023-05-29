#!/usr/bin/env python

"""
Script uses the CB REST API to delete a resource based on the
arguments passed to it.

Sample usage to delete resource of type service with ID 108:

    delete_resource.py \
        --username user --password passw --token token --domain domain \
        --host cb-ip-or-host  --port port --protocol http \
        --resource-id 108 \
        --resource-type service \
        --wait
"""
from __future__ import print_function
from __future__ import absolute_import


import json
import os
import sys

# Add samples directory to path so we can import api_helpers
samples_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, samples_dir)

from api_helpers import (
    update_pythonpath,
    wait_for_job_completion,
    wait_for_order_completion,
    BaseAPIArgParser,
    submit_order,
    approve_order,
)

update_pythonpath()
from api_client import CloudBoltAPIClient

WAIT_TIMEOUT_SEC = 60 * 60
# How long to wait before polling
WAIT_INTERVAL_SEC = 10


def get_delete_resource_url(cb, resource_id, resource_type_name):
    """
    Given a resource ID & its type, gets the representation of that resource from the API and
    finds the URL that can be used to run the Delete action on that
    resource
    """
    response = cb.get(
        "/api/v2/resources/{resource_type_name}/{resource_id}/".format(
            resource_type_name=resource_type_name, resource_id=resource_id
        )
    )
    response = json.loads(response)
    print("Response to GET the resource:\n", response)
    actions = response["_links"]["actions"]
    for action in actions:
        if "Delete" in action:
            delete_url = action["Delete"]["href"]
            break

    return delete_url


class ArgParser(BaseAPIArgParser):
    def add_arguments(self, parser):
        # Supplement the default connection arguments with ones specific to this method.
        parser.add_argument(
            "--resource-id", required=True, help="ID of resource to be deleted"
        )
        parser.add_argument(
            "--resource-type", required=True, help="Name of the type of the resource"
        )
        parser.add_argument(
            "--wait",
            action="store_true",
            help="Wait until job completes; time out after {wait} seconds".format(
                wait=WAIT_TIMEOUT_SEC
            ),
        )


if __name__ == "__main__":
    args = ArgParser().parse()
    cb = CloudBoltAPIClient(**vars(args))

    delete_url = get_delete_resource_url(cb, args.resource_id, args.resource_type)
    print("URL to delete resource: {}".format(delete_url))
    response = cb.post(delete_url)
    response = json.loads(response)
    print("Response to POST to delete resource: {response}".format(response=response))

    response_url = response["run-action-job"]["self"]["href"]
    # The object in the response could be either a Job (the default) or an Order (if the "Delete" Resource Action
    # is set to require approval)
    job_prefix = "/api/v2/jobs/"
    job_id = None
    order_prefix = "/api/v2/orders/"
    order_id = None
    if response_url.startswith(job_prefix):
        job_id = response_url.replace(job_prefix, "").strip("/")
        print("Started Delete Resource Job with ID {job_id}".format(job_id=job_id))

    elif response_url.startswith(order_prefix):
        order_id = response_url.replace(order_prefix, "").strip("/")
        # Submit and approve the order, otherwise it just sits in the cart
        order = submit_order(cb, order_id)
        if order.get("status", "") == "PENDING":
            order = approve_order(cb, order_id)
        # Here we expect the order to be approved; if not,
        # something in this group or environment is misconfigured and manual
        # intervention is required.
        if order.get("status", "") != "ACTIVE":
            sys.exit(
                "Failure: The submitted order is not active. Please ensure "
                "that the user has approval permission on this group or that "
                "auto-approval is enabled for this group or environment."
            )
        print(
            "Started Delete Resource Order with ID {order_id}".format(order_id=order_id)
        )

    else:
        sys.exit(
            "Failure: The returned value was neither a Job nor an Order. Please report"
            "this issue to your Administrator."
        )

    if args.wait:
        # If job/ order completes, exits with status code 0; otherwise with code 1
        # and a message indicating why.
        if job_id:
            sys.exit(
                wait_for_job_completion(cb, job_id, WAIT_TIMEOUT_SEC, WAIT_INTERVAL_SEC)
            )
        else:
            sys.exit(
                wait_for_order_completion(
                    cb, order_id, WAIT_TIMEOUT_SEC, WAIT_INTERVAL_SEC
                )
            )
