#!/usr/bin/env python

"""
Script uses the CB REST API to order a blueprint based on the arguments passed to it.
"""
from __future__ import print_function
from __future__ import absolute_import


EXAMPLE_USAGE = """
Sample usage to deploy a simple blueprint:

    order_blueprint.py
        --username user --password passw [--token token] [--domain domain]
        --host cb-ip-or-host  --port port --protocol https
        --group-id    group-id
        [--owner-id    user-id]
        [--recipient-id    user-id]
        --deploy-items '[
             {
                 "blueprint": "/api/v2/blueprints/<blueprint-global-id>",
                 "blueprint-items-arguments": {
                     "build-item-<blueprint item name>": {
                         "environment": "/api/v2/environments/<env-global-id>",
                         "attributes": {
                             "quantity": 1
                         },
                         "parameters": {
                             "sc-nic-0": "<network name>",
                             "cpu-cnt": "1",
                         },
                         "os-build": "/api/v2/os-builds/<os-build-global-id>"
                     }
                 },
                 "resource-name": ""
             }
         ]'

The best way to figure out the "deploy-items" is to submit a similar order in the CB UI,
then click the "API..." button on the order details page. The dialog that appears will contain
the body of the request, from which you can copy and paste the list of deploy-items, then change
the parameters to fit your needs.

If you would like to use this to order a custom server, pass the Global ID of the blueprint called
"Custom Server", along with any parameters that are relevant for the chosen group and environment.

The ID provided for the Group can be either its Global ID (recommended due to consistency across
CloudBolt instances) or primary key ID.
"""

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


def create_order(cb, deploy_items, group_id, owner_id=None, recipient_id=None):
    """
    Starts a new order on the cb connection.
    Optionally sets the owner to the User with ID=owner_id.
    Optionally sets the recipient to the User with ID=recipient_id.

    Returns both the response, which is a representation of the order, and the
    order ID.
    """
    print("Creating order for group {0}...".format(group_id))
    body = {"group": "/api/v2/groups/{0}".format(group_id)}

    if owner_id:
        body["owner"] = "/api/v2/users/{0}".format(owner_id)
        print("... and owner {0}".format(owner_id))
    if recipient_id:
        body["recipient"] = "/api/v2/users/{}".format(recipient_id)
        print("... with recipient {}".format(recipient_id))

    body["items"] = {"deploy-items": deploy_items}

    body["submit-now"] = "true"
    raw_response = cb.post("/api/v2/orders/", json.dumps(body))

    response = json.loads(raw_response)
    if "status_code" in response and not 200 <= response["status_code"] < 300:
        error = pretty_print(response)
        print("Error creating order through the API: {0}".format(error))
        sys.exit(1)

    order_url = response["_links"]["self"]["href"]
    order_id = order_url.replace("/api/v2/orders/", "").strip("/")

    print("Order {} created.".format(order_id))
    return response, int(order_id)


class ArgParser(BaseAPIArgParser):
    def add_arguments(self, parser):
        # Supplement the default connection arguments with ones specific to this method.

        # required order args
        parser.add_argument(
            "--group-id",
            help=(
                "Group ID for the order, which can be either its "
                "Global ID (recommended) or primary key ID."
            ),
            required=True,
        )
        # optional order args
        parser.add_argument(
            "--owner-id",
            help=(
                "ID of user that will be the owner of the order ("
                "only needed if different from the API user, who "
                "is the default order owner). The API user must "
                "be a super admin to use this option."
            ),
        )
        parser.add_argument(
            "--recipient-id",
            help=(
                "ID of user that will be the owner of the Server(s) "
                "and/or Resource(s) created by the order (only "
                "needed if different from the order owner, who "
                "owns them by default). The API user must have "
                "the order.choose_recipient permission in the "
                "group to use this option. The selected recipient "
                "must have the order.submit permission in the group."
            ),
        )
        parser.add_argument(
            "--wait",
            action="store_true",
            help="Wait until order completes; time out after {wait} seconds".format(
                wait=WAIT_TIMEOUT_SEC
            ),
        )
        parser.add_argument(
            "--deploy-items",
            help="JSON list that should contain a single dictionary describing the blueprint to "
            "be deployed. This can be copied from the CB UI under Admin > API browser > "
            "Orders.",
            required=True,
        )

    def parse(self):
        args = super(ArgParser, self).parse()
        args.deploy_items = json.loads(args.deploy_items)
        return args


if __name__ == "__main__":
    args = ArgParser().parse()
    cb = CloudBoltAPIClient(**vars(args))

    order, order_id = create_order(
        cb, args.deploy_items, args.group_id, args.owner_id, args.recipient_id
    )

    if order.get("status", "") == "PENDING":
        # If it's awaiting approval, that must mean it was not auto-approved and, if there was an
        #  order approval hook, it did not approve it. Attempt to approve now.
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
