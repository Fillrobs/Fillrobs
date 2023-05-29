"""
Calculates the rate for the chosen GCE node size.

Rate is displayed in the units chosen in Rates Options.

Deprecated as of 2019 with the addition of the GCP resource handler.
"""


from decimal import Decimal
import os.path
import json

from django.conf import settings

from costs.utils import default_compute_rate
from resourcehandlers.gce.models import GCEHandler
from utilities.helpers import cb_request
from utilities.logger import ThreadLogger
from utilities.models import GlobalPreferences

NUMBER_OF_HOURS = {
    "HOUR": 1,
    "DAY": 24,
    "WEEK": 192,
    "MONTH": 720,  # assumes 30-day month
    "YEAR": 8760,  # assumes 365-day year
}
GCE_URL = "https://cloudpricingcalculator.appspot.com/static/data/pricelist.json"
FILE_PATH = "{}opt/cloudbolt/gce_pricing_data.json".format(settings.VARDIR)

logger = ThreadLogger(__name__)


def download_file(url, file_location):
    """
    Downloads the pricing file for the given json url and saves it to the given directory
    if the file does not already exist.
    """
    if os.path.exists(file_location):
        return

    logger.debug("Downloading pricing file from {}".format(url))
    r = cb_request("GET", url, stream=True)
    with open(file_location, "wb") as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
    logger.debug("Download complete")


def _compute_gce_rate(environment, node_size):
    """
    This is the part that makes the API calls to GCE to download the rate
    file and parses that for the rate of the given node size.

    This method contains all the external API calls to GCE for easy mocking, which is
    done in cbhooks/tests/test_rate_hooks.py
    """
    image_key = "CP-COMPUTEENGINE-VMIMAGE-{}".format(node_size.upper())

    download_file(GCE_URL, FILE_PATH)

    with open(FILE_PATH) as f:
        json_data = json.load(f)

    rh = GCEHandler.objects.first()
    location = rh.get_env_location(environment)
    region = location.split("-")[0]  # e.g. the "us" in "us-central1-a"

    price_list = json_data["gcp_price_list"]
    rate = price_list[image_key][region]

    rate_time_unit = GlobalPreferences.objects.get().rate_time_unit
    number_of_hours = NUMBER_OF_HOURS.get(rate_time_unit, 0)

    return number_of_hours, rate


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
        # This is also useful for testing to check whether we returned rates just from GCE.
        logger.info("Only including GCE-specific rates from the GCE rate hook.")
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
        # rate from GCE.
        rate_dict.update({"Hardware": {}})
        logger.info("Including the default Admin/rates in the GCE rate hook.")

    node_size = None
    for cfv in cfvs:
        if cfv.field.name == "node_size" and cfv.value:
            node_size = cfv.value
            break

    if not node_size:
        logger.warning(
            "Can't calculate rate because node size couldn't be " "determined."
        )
        return rate_dict

    number_of_hours, rate = _compute_gce_rate(environment, node_size)
    rate_dict.update(
        {"Hardware": {"Node Size": Decimal(rate) * number_of_hours * quantity}}
    )

    return rate_dict
