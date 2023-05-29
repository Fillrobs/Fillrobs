from common.methods import set_progress
from orders.models import Order
from utilities.servicenow_api import ServiceNowAPI

"""
ServiceNow Service Request Queue
~~~~~~~~~~~~~~~~~~~~~~~~~
Syncs CloudBolt Order Approval status with ServiceNow Approval status.
Based off of unique id sent to ServiceNow when Order is submitted.

Version Req.
~~~~~~~~~~~~
CloudBolt 9.0
"""

#########################
### Settings Override ###

### Status Options ###
"""
Response field from ServiceNow.
'stage', 'request_state', 'approval' are options often used.
'approval' is default setting
'order_approve' and 'order_deny' are CloudBolt specific and required.
Example: status_levels = {'order_approve':{'approval': ['approved']},'order_deny':{'approval': ['rejected']}}
"""

### ServiceNow Approval Status Field ###
"""
set_approval_field()
Default is 'approval'
Example: ServiceNowAPI().set_approval_field('stage')
"""


def run(job=None, logger=None, **kwargs):

    set_progress("Running Remedy ticket queue manager")

    # Get all PENDING orders
    pending_orders = Order.objects.filter(status="PENDING")

    # If there are any pending orders, begin calling ServiceNow for the corresponding order item
    if pending_orders:

        servicenow = ServiceNowAPI()

        # Override CloudBolt ServiceNow status checks here
        # servicenow.set_status_option(status_levels=status_levels)
        # servicenow.set_approval_field('approval')

        """
        Loop through pending orders which have a PENDING status.
        Update status to be the status which has been set in ServiceNow
        """
        for order in pending_orders:
            # Here we get the first order item as this is the one we're using to tag the ServiceNow.sc_request.sys_id attribute
            order_item = order.orderitem_set.first()
            bp_order_item = order_item.blueprintorderitem
            # update order status. Default to pending.
            status_message = servicenow.update_order_status(bp_order_item)

            set_progress(f"{status_message}")

    return "SUCCESS", "", ""
