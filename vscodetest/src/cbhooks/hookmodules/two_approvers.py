"""
Two User Approval
~~~~~~~~~~~~~~~~~
Overrides CloudBolt's standard Order Approval workflow. This Orchestration
Action requires two users approve an Order before it becomes Active.


Version Req.
~~~~~~~~~~~~
CloudBolt 8.8
"""


def run(order, *args, **kwargs):
    # If fewer than two users have approved this order, we'll call the
    # `set_pending()` method, which returns to order to the queue for other
    # users to approve or deny.
    if len(order.approvers) < 2:
        order.set_pending()

    return "SUCCESS", "", ""
