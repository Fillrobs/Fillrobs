"""
Hook to add Service Catalog Request Record for Order when submitted.
Can be managed through the CloudBolt ServiceNow Management page.
"""
from utilities.servicenow_api import ServiceNowAPI
from utilities.logger import ThreadLogger
from orders.models import BlueprintOrderItem

logger = ThreadLogger("Service Now Order Submit")


def run(order=None, *args, **kwargs):
    order_item = order.orderitem_set.first()

    try:
        if not isinstance(order_item.cast(), BlueprintOrderItem):
            logger.warning(
                "No BluePrint associate with this order item: ServiceNow Service Catalog record will not be created."
            )
            return "SUCCESS", "", ""
        bp_order_item = order_item.blueprintorderitem
    except AttributeError as e:
        logger.warning(f"Could not find BluePrintOrderItem: {e}.")
        # Returning Success here if no BP Item. We need a BP item to pin a custom value param too.
        # If no BP exists, it's most likely a decom job anyway
        return "SUCCESS", "", ""

    service_now_api = ServiceNowAPI()
    result = service_now_api.create_service_catalog_record(bp_order_item=bp_order_item)

    if result:
        return "SUCCESS", "", ""
    else:
        return "FAILURE", "ServiceNow Service Record not created", ""
