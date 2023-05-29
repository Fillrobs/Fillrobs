#!/usr/bin/env python

"""
Script uses the CB REST API to decommission one or more servers based on the
arguments passed to it.

Sample usage to decommission servers with ID 108 and 356:

    decom_server.py \
        --username user --password passw --token token --domain domain \
        --host cb-ip-or-host --port port --protocol http \
        --group-id    GRP-a123b456 \
        --env-id      ENV-123a456b \
        --server-ids 108 356 \
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
    BaseAPIArgParser,
    wait_for_order_completion,
    approve_order,
    pretty_print,
)

update_pythonpath()
from api_client import CloudBoltAPIClient


# A resource handler on CB may also have a timeout configured based on how
# long builds ought to take; here, a timeout simply gives this script the
# option to be less patient.
WAIT_TIMEOUT_SEC = 60 * 60
# How long to wait before polling
WAIT_INTERVAL_SEC = 10


def decom_order_item_dict(env_id, server_ids):
    """
    Helper function to build a dict representing a server decom order item.
    """
    order_item = {
        "environment": "/api/v2/environments/{env_id}".format(env_id=env_id),
        "servers": [],
    }

    for server_id in server_ids:
        order_item["servers"].append(
            "/api/v2/servers/{server_id}".format(server_id=server_id)
        )
    return order_item


def create_order(cb, group_id, decom_item):
    """
    Starts a new order on the cb connection.

    Returns both the response, which is a representation of the order, and the
    order ID.
    """
    print("Creating order for group {0}...".format(group_id))
    body = {"group": "/api/v2/groups/{0}".format(group_id)}

    body["items"] = {"decom-items": [decom_item]}
    body["submit-now"] = "true"
    raw_response = cb.post("/api/v2/orders/", json.dumps(body))

    response = json.loads(raw_response)
    if "status_code" in response and not 200 <= response["status_code"] < 300:
        error = pretty_print(response)
        print("Error creating order through the API: {0}".format(error))
        sys.exit(1)

    order_url = response["_links"]["self"]["href"]
    order_id = order_url.replace("/api/v2/orders/", "").strip("/")

    print("Order {order_id} created.".format(order_id=order_id))
    return response, int(order_id)


class ArgParser(BaseAPIArgParser):
    def add_arguments(self, parser):
        # Supplement the default connection arguments with ones specific to this method.
        parser.add_argument(
            "--group-id",
            required=True,
            help="Group ID for server, which can be either its "
            "Global ID (recommended) or primary key ID.",
        )
        parser.add_argument(
            "--env-id",
            required=True,
            help="Environment ID for server, which can be either its "
            "Global ID (recommended) or primary key ID.",
        )
        parser.add_argument(
            "--server-ids",
            required=True,
            nargs="*",
            help="One or more IDs of servers to be decommissioned",
        )
        parser.add_argument(
            "--wait",
            action="store_true",
            help="Wait until order completes; time out after {wait} seconds".format(
                wait=WAIT_TIMEOUT_SEC
            ),
        )


if __name__ == "__main__":
    args = ArgParser().parse()
    cb = CloudBoltAPIClient(**vars(args))

    order_item = decom_order_item_dict(args.env_id, args.server_ids)
    order, order_id = create_order(cb, args.group_id, order_item)

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

    if args.wait:
        # If order completes, exits with status code 0; otherwise with code 1
        # and a message indicating why.
        sys.exit(
            wait_for_order_completion(cb, order_id, WAIT_TIMEOUT_SEC, WAIT_INTERVAL_SEC)
        )
