"""
Hook to add Service Catalog Request Record for Order when submitted.
Can be managed through the CloudBolt ServiceNow Management page.
"""
from utilities.logger import ThreadLogger
from orders.models import BlueprintOrderItem

logger = ThreadLogger("Service Now Order Submit")


def create_service_catalog_record(itsm, order=None):
    """
    Creates a new service catalog entry which will need to have status approved.
    :param order: Order object
    """
    if not order:
        return False

    # Set the ServiceNow item to reference a single order item.
    # This is done because Custom Value Params are not set on the order level.
    order_item = order.orderitem_set.first()

    try:
        if not isinstance(order_item.cast(), BlueprintOrderItem):
            logger.warning(
                "No BluePrint associate with this order item: ServiceNow Service Catalog record will not be created."
            )
            return True
        bp_order_item = order_item.blueprintorderitem
    except AttributeError as e:
        logger.warning(f"Could not find BluePrintOrderItem: {e}.")
        # Returning True here if no BP Item. We need a BP item to pin a custom value param too.
        # If no BP exists, it's most likely a decom job anyway
        return True

    service_now_api = itsm.get_api_wrapper()
    result = service_now_api.create_service_catalog_record(bp_order_item=bp_order_item)

    if result:
        return True
    else:
        return False
