"""
Calculates the rate for the chosen GCP node size.

Rate is displayed in the units chosen in Rates Options.
"""


from decimal import Decimal
import os.path
import json

from django.conf import settings

from utilities.helpers import cb_request
from utilities.logger import ThreadLogger
from utilities.models import GlobalPreferences
from utilities.exceptions import CloudBoltException

NUMBER_OF_HOURS = {
    "HOUR": 1,
    "DAY": 24,
    "WEEK": 168,
    "MONTH": 720,  # assumes 30-day month
    "YEAR": 8760,  # assumes 365-day year
}
GCP_URL = "https://cloudpricingcalculator.appspot.com/static/data/pricelist.json"
FILE_PATH = "{}opt/cloudbolt/gcp_pricing_data.json".format(settings.VARDIR)
DEFAULT_GCP_ZONE = "us"

logger = ThreadLogger(__name__)


def download_file(url, file_location):
    """
    Downloads the pricing file for the given json url and saves it to the given directory
    if the file does not already exist.
    """
    if os.path.exists(file_location):
        logger.debug("Using existing data at {}".format(file_location))
        return

    logger.debug("Downloading pricing file from {}".format(url))
    r = cb_request("GET", url, stream=True)
    if r.status_code >= 400:
        raise CloudBoltException(
            "Unable to download GCP rates; pricing data URL {url} returned bad status code {code}.".format(
                url=url, code=r.status_code,
            )
        )
    with open(file_location, "wb") as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
    logger.debug("Download complete")


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
    gcp_zone = DEFAULT_GCP_ZONE
    node_size = None
    for cfv in cfvs:
        if "node_size" in cfv.field.name and cfv.value:
            node_size = cfv.value
        if "gcp_zone" in cfv.field.name and cfv.value:
            gcp_zone = "-".join(cfv.value.split("-")[0:2])
        if gcp_zone and node_size:
            break

    # If we cannot determine the node size, we cannot calculate a rate
    if not node_size:
        logger.warning("GCP Node Size could not be determined for rate calculation.")
        return {}

    # If we cannot determine a zone, default to generic US zone
    if not gcp_zone:
        logger.warning(
            "Could not determine GCP Zone to calculate rate for {node_size}. Falling back on {default_zone}.".format(
                node_size=node_size, default_zone=gcp_zone
            )
        )

    try:
        download_file(GCP_URL, FILE_PATH)
    except CloudBoltException as e:
        logger.warning(e)
        return {}

    with open(FILE_PATH) as f:
        json_data = json.load(f)

    # Get all prices in the response data
    price_list = json_data.get("gcp_price_list")
    if not price_list:
        logger.warning(
            "Could not locate GCP Price List to calculate rate for node size {node_size}.".format(
                node_size=node_size
            )
        )
        return {}

    # Get all rates for this node size
    image_key = "CP-COMPUTEENGINE-VMIMAGE-{}".format(node_size.upper())
    node_rates = price_list.get(image_key)
    if not node_rates:
        logger.warning(
            "Could not locate GCP rates for node size {node_size}.".format(
                node_size=node_size
            )
        )
        return {}

    # Get this specific node+region rate
    rate = node_rates.get(gcp_zone)
    if not rate:
        logger.warning(
            "Could not determine rate for node size {node_size} in zone {gcp_zone}.".format(
                node_size=node_size, gcp_zone=gcp_zone
            ),
        )
        return {}

    rate_time_unit = GlobalPreferences.objects.get().rate_time_unit
    number_of_hours = NUMBER_OF_HOURS.get(rate_time_unit, 0)
    rate_for_node_order = Decimal(rate) * number_of_hours * quantity
    return {
        "Hardware": {"Node Size": round(rate_for_node_order, 2)},
    }
