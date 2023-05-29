"""
Calculates the on-demand rate for the chosen IBM instance type.

Rate is displayed in the time units chosen in Rates Options. Assumes the
currency is USD, edit this action to change it.

This file is applied when provisioning a server.
These rates are updated regularly by the 'Refresh Server Rates' recurring job.
"""


from decimal import Decimal
import os.path  # noqa: F401
import ijson  # noqa: F401
import json  # noqa: F401
import time  # noqa: F401
import re  # noqa: F401
import requests  # noqa: F401

import SoftLayer  # noqa: F401

from costs.utils import default_compute_rate
from utilities.logger import ThreadLogger
from utilities.models import GlobalPreferences  # noqa: F401

NUMBER_OF_HOURS = {
    "HOUR": 1,
    "DAY": 24,
    "WEEK": 192,
    "MONTH": 720,  # assumes 30-day month
    "YEAR": 8760,  # assumes 365-day year
}

logger = ThreadLogger(__name__)


def get_price(environment, ibm_instance_type):
    resource_handler = environment.resource_handler
    client = resource_handler.cast().api

    total_price = 0
    standard_price = 0
    packageId = 835

    objectMask = "mask[prices[item]]"
    objectMaskPrice = "mask[pricingLocationGroup[locations]]"

    activePresets = client["SoftLayer_Product_Package"].getActivePresets(
        id=packageId, mask=objectMask
    )
    preset = (
        [preset for preset in activePresets if preset["name"] == ibm_instance_type]
        or [None]
    )[0]

    try:
        for prices in preset["prices"]:
            objectFilterItem = {
                "itemPrices": {"item": {"id": {"operation": prices["item"]["id"]}}}
            }
            prices = client["SoftLayer_Product_Package"].getItemPrices(
                id=packageId, filter=objectFilterItem, mask=objectMaskPrice
            )
            for price in prices:
                if (
                    "pricingLocationGroup" in price
                    and price.get("pricingLocationGroup") is not None
                ):
                    locations = price.get("pricingLocationGroup").get("locations")

                    if environment.slayer_datacenter in [
                        location.get("name") for location in locations
                    ]:
                        total_price += float(price.get("recurringFee"))
                else:
                    standard_price += float(price.get("recurringFee"))
    except Exception:
        total_price == 0

    if total_price == 0:
        total_price = standard_price
    return total_price


def compute_rate(
    group,
    environment,
    resource_technology,
    cfvs,
    pcvss,
    os_build,
    apps,
    quantity=1,
    **kwargs,
):

    override_defaults = kwargs.pop("override_defaults", False)

    if override_defaults:
        # This is also useful for testing to check whether we returned rates just from IBM.
        logger.info("Only including IBM-specific rates from the IBM rate hook.")
        rate_dict = {}
    else:
        # The rate_dict below will include any Software or Extra rates from the Admin/Rates settings.
        # You can modify this file to exclude these rates.
        rate_dict = default_compute_rate(
            group,
            environment,
            resource_technology,
            cfvs,
            pcvss,
            os_build,
            apps,
            quantity,
            **kwargs,
        )
        # Override Hardware rates for consistency; so that we don't return the
        # default CPU/Disk Rates, which would be misleading about whether we got the
        # rate from IBM.
        rate_dict.update({"Hardware": {}})
        logger.info("Including the default Admin/rates in the IBM rate hook.")

    ibm_instance_type = None
    for cfv in cfvs:
        if cfv.field.name == "ibm_instance_type":
            ibm_instance_type = cfv.value

    if not ibm_instance_type:
        logger.warning(
            "Can't calculate rate because instance type couldn't be " "determined."
        )
        return rate_dict

    rate = get_price(environment, ibm_instance_type)

    rate_dict.update({"Hardware": {"IBM Instance Type": Decimal(rate)}})
    return rate_dict
