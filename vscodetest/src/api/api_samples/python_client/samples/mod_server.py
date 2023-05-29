#!/usr/bin/env python

"""
Script uses the CB REST API to modify a server based on the arguments
passed to it. Modifications can include changes to resources (CPU & memory) or
resizing disks
"""
from __future__ import print_function
from __future__ import absolute_import

EXAMPLE_USAGE = """
Sample usage to modify a VM:

    mod_server.py
        --username user --password passw [--token token] [--domain domain]
        --host cb-ip-or-host  --port port --protocol https
        --server-id   server-id
        --group-id    group-id
        --env-id      env-id
        [--owner-id   user-id for the user to own this order]
        --cf
            cpu_cnt=2
            mem_size=4
            disk_size=20
            new_disk_size=10
        [--disk-uuid 6000C292-e813-90a3-c88d-0aef0e8c4673]

The cf can be any of the options listed; it does not need to be all of them.

The disk-uuid is only necessary if you've included disk_size under cf in order
to resize/ extend a disk. The UUID for the disk you wish to make bigger can be
found by looking at the appropriate dictionary under the disks section of the
server's serialization, or on the server's Disks tab in the UI. Passing
disk_size without a disk-uuid will not work.
"""
# TODO: fetch the group & env ID from the server instead of making the user specify them
# TODO: enable modification of NICs and attributes on the server (or that could be a
# separate sample script)

import json
import os
import sys

# Add samples directory to path so we can import api_helpers
samples_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, samples_dir)

from api_helpers import (
    create_order_for_group,
    submit_order,
    update_pythonpath,
    wait_for_order_completion,
    approve_order,
    BaseAPIArgParser,
)

update_pythonpath()
from api_client import CloudBoltAPIClient


# A resource handler on CB may also have a timeout configured based on how
# long builds ought to take; here, a timeout simply gives this script the
# option to be less patient.
WAIT_TIMEOUT_SEC = 60 * 10
# How long to wait before polling
WAIT_INTERVAL_SEC = 10


def mod_order_item_dict(env_id, server_id, parameters={}, disk_uuid=None):
    """
    Helper function to build a dict representing a server modification order item.
    """
    order_item = {
        "server": "/api/v2/servers/{0}".format(server_id),
        "environment": "/api/v2/environments/{0}".format(env_id),
    }
    if parameters:
        order_item["parameters"] = parameters
    if disk_uuid:
        order_item["disk-uuid"] = disk_uuid
    return order_item


def add_mod_order_item(cb, order_id, mod_item):
    """
    Creates a new "modify server" order item on specified order.
    Args:
        order_id
        mod_item: dict representing server modification order item
            See API docs for samples.
    """
    print("Adding order item to order {0}...".format(order_id))
    print(json.dumps(order_item, indent=4))
    response = cb.post(
        "/api/v2/orders/{0}/mod-items/".format(order_id), body=json.dumps(mod_item)
    )
    print("Response:\n", response)
    return response


class ArgParser(BaseAPIArgParser):
    def add_arguments(self, parser):
        # Supplement the default connection arguments with ones specific to this method.
        parser.add_argument(
            "--owner-id", help="ID of user that will be the order's owner"
        )
        parser.add_argument(
            "--group-id",
            help="Group ID for server, which can be either its "
            "Global ID (recommended) or primary key ID.",
            required=True,
        )
        parser.add_argument(
            "--env-id",
            help="Environment ID for server, which can be either its "
            "Global ID (recommended) or primary key ID.",
            required=True,
        )
        parser.add_argument("--server-id", help="CloudBolt Server ID")
        parser.add_argument(
            "--cf",
            dest="parameters",
            nargs="*",
            help="List of custom field (AKA parameter) name=value pairs",
        )
        parser.add_argument(
            "--disk-uuid", help="UUID of disk to modify, if passing disk_size"
        )
        parser.add_argument(
            "--wait",
            action="store_true",
            help="Wait until order completes; time out after {wait} seconds".format(
                wait=WAIT_TIMEOUT_SEC
            ),
        )

    def parse(self):
        args = super(ArgParser, self).parse()
        args.parameters = self.parameter_kwarg_strings_to_dict(args.parameters)
        return args


if __name__ == "__main__":
    args = ArgParser().parse()
    cb = CloudBoltAPIClient(**vars(args))

    order_id = create_order_for_group(cb, args.group_id, args.owner_id)

    order_item = mod_order_item_dict(
        args.env_id, args.server_id, args.parameters, args.disk_uuid
    )

    add_mod_order_item(cb, order_id, order_item)

    order = submit_order(cb, order_id)
    if order.get("status", "") == "PENDING":
        order = approve_order(cb, order_id)

    # Here we expect the order to be approved; if not,
    # something in this group or environment is misconfigured and manual
    # intervention is required.
    if order["status"] != "ACTIVE":
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
