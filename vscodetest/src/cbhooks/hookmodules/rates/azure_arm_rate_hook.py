"""
Calculates the rate for the chosen Azure Resource Manager node size.

This is a sample hook that comes with various limitations.
* Only concerns itself with node size and OS
* Assumes use of the Pay-As-You-Go offer
* Assumes US region and USD currency
* Assumes Azure rates are given in $/hr (true as of 9/2016)

In addition, the Azure API often returns multiple rates per node size. We
conservatively pick the most expensive out of the most recent rate set.

Rate is displayed in the units chosen in Rates Options.
"""
import re

from azure.mgmt.commerce.models import MeterInfo  # noqa: F401
from django.core.cache import cache

from decimal import Decimal

from costs.utils import default_compute_rate
from infrastructure.models import Environment  # noqa: F401
from resourcehandlers.azure_arm.models import (  # noqa: F401
    AzureARMHandler,
    AzureMeter,
    METER_REGIONS,
)
from utilities.logger import ThreadLogger
from utilities.models import GlobalPreferences

NUMBER_OF_HOURS = {
    "HOUR": 1,
    "DAY": 24,
    "WEEK": 192,
    "MONTH": 730,  # average hours per month
    "YEAR": 8760,  # assumes 365-day year
}

logger = ThreadLogger(__name__)


def node_size_to_meter_name_and_sub_category(node_size, is_windows=False):
    logger.info(f"Parsing node size {node_size} to get meter_name and sub_category")

    # Split out the node size
    if not node_size or "_" not in node_size:
        return None, None
    basic_or_standard, raw_series, *versions = node_size.split("_")

    sub_category = raw_series
    meter_name = raw_series

    if basic_or_standard == "Basic":
        sub_category = re.sub(r"[0-9]+", "", sub_category)
        sub_category += " Series Basic"
    elif basic_or_standard == "Standard":
        # Remove embellishments from the node size that are not used in sub categories
        # and do not affect meter rates.
        # Example: 'E32-16ms' -> 'E'
        sub_category_embellishments = [r"[0-9]+", "-", "m", "r"]
        for pattern in sub_category_embellishments:
            sub_category = re.sub(pattern, "", sub_category)
        sub_category = sub_category.upper()

        # Remove embellishments from the node size that are not used in meter names and
        # do not affect meter rates.
        # example: 'E32-8s' -> 'E32s'
        meter_name_embellishment = r"-[0-9]+"
        meter_name = re.sub(meter_name_embellishment, "", meter_name)

        # Append versions to the sub_category and meter_name
        if len(versions) > 0:
            # example: if versions = ['v2', 'Promo'], then appends the string 'v2 Promo' to the sub_category.
            # or if versions = ['Promo'], appends ' Promo'
            # For meter_names, only versions get included, so exclude 'Promo' completely.
            if versions == ["Promo"]:
                sub_category += " Promo"
            else:
                sub_category += " ".join(versions)
                meter_name += (
                    f" {versions[0]}"  # This should now only be a version, like 'v2'
                )

        sub_category += " Series"

    if is_windows:
        sub_category += " Windows"

    logger.info(
        f"Determined meter_name: '{meter_name}' and sub_category: '{sub_category}'"
    )

    return meter_name, sub_category


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
    """
    Finds a rate for the selected node size and os_build (windows or non-windows) and returns
    a dictionary containing information about the cost of the VM.
    """
    override_defaults = kwargs.pop("override_defaults", False)

    if override_defaults:
        # This is also useful for testing to check whether we returned rates just from Azure.
        logger.info("Only including Azure-specific rates from the Azure rate hook.")
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
        # rate from Azure.
        rate_dict.update({"Hardware": {}})
        logger.info("Including the default Admin/rates in the Azure rate hook.")

    # Get the node size CFV or return None, because we can't calculate rates without a node size.
    node_size = None
    for cfv in cfvs:
        if cfv.field.name == "node_size" and cfv.value:
            node_size = cfv.value
            break
    if not node_size:
        # This rarely happens, but we can't calculate rate without node size.
        logger.warning("No node size, cannot calculate Azure rate without a node size.")

        return rate_dict

    # Get the resource handler from the environment or just grab the first one.
    rh = environment.resource_handler
    if not rh:
        # This will happen for synced servers which are automatically assigned to the 'Unassigned' env,
        # so default to the 1st ARM handler.
        rh = AzureARMHandler.objects.first()
    rh = rh.cast()

    # Determine whether or not this instance is windows.
    try:
        is_windows = os_build.os_family.name == "Windows"
    except AttributeError:
        logger.info(
            "OS build couldn't be detected, so the rate will assume "
            "it is not Windows."
        )
        is_windows = False

    # Get the sub-category for the meter by the old (pre-Aug 2018) naming conventions.
    meter_name, sub_category = node_size_to_meter_name_and_sub_category(
        node_size, is_windows
    )

    if not meter_name or not sub_category:
        logger.warning(
            f"Could not parse node size '{node_size}' into a meter name or sub category."
        )
        return rate_dict

    # Try to get the rate for this sub-category from the cache to avoid getting the whole rate card.
    cache_key = f"{sub_category}_{meter_name}".replace(" ", "_")
    rate = cache.get(cache_key)

    if rate:
        logger.info("Using cached rate {} for {}".format(rate, node_size))
    else:
        meter = rh.find_matching_vm_meter(
            environment, meter_name, sub_category, is_windows
        )

        if meter is None:
            logger.warning(
                "Expected to find rates for sub category '{}' and meter name '{}', but none were found.".format(
                    sub_category, meter_name
                )
            )
            return rate_dict
        logger.info(f"Using rate from meter info: '{vars(meter)}'.")

        rate = str(meter.meter_rates["0"])
        cache.set(cache_key, rate)

    rate_time_unit = GlobalPreferences.objects.get().rate_time_unit
    number_of_hours = NUMBER_OF_HOURS.get(rate_time_unit, 0)
    label = "Node Size"
    if is_windows:
        label += " (Windows)"

    azure_rate_dict = {
        "Hardware": {label: Decimal(rate) * number_of_hours * quantity},
    }

    rate_dict.update(azure_rate_dict)

    return rate_dict
