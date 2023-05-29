#!/usr/bin/env python
"""
Compares the last modified date of both the local file where rate data is stored and the last modified date of the
source url.
If the source has been updated since the last file download,
the newer rate files are downloaded and server rates are updated with the new data.
"""
import ijson
import json
import os.path

from datetime import datetime

from django.conf import settings
from ijson.common import IncompleteJSONError

from infrastructure.models import Server
from utilities.filesystem import mkdir_p
from utilities.helpers import cb_request
from utilities.logger import ThreadLogger
from utilities.models import GlobalPreferences

AWS_URL = "https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonEC2/current/index.json"
AWS_RATE_HOOK_DIR = "{}opt/cloudbolt/aws_rate_hook".format(settings.VARDIR)
aws_file_location = "{}/full_pricing_data.json".format(AWS_RATE_HOOK_DIR)

GCE_URL = "https://cloudpricingcalculator.appspot.com/static/data/pricelist.json"
GCE_RATE_HOOK_DIR = "{}opt/cloudbolt".format(settings.VARDIR)
gce_file_location = "{}opt/cloudbolt/gce_pricing_data.json".format(settings.VARDIR)

GCP_URL = GCE_URL
GCP_RATE_HOOK_DIR = GCE_RATE_HOOK_DIR
gcp_file_location = "{}opt/cloudbolt/gcp_pricing_data.json".format(settings.VARDIR)

logger = ThreadLogger(__name__)


def check_for_update(file_location, url):
    """
    Compares the last modified date of the file and that of the request.
    Returns the boolean 'update' for whether the rates need to be updated on servers of the given resource tech.

    :param file_location:
    :param url:
    :return update:
    """
    # get the last modified date of the file, if it exists
    try:
        local_updated = datetime.utcfromtimestamp(os.path.getmtime(file_location))
    except OSError:  # the file doesn't exist yet
        logger.debug(
            'Rate file does not exist at "{}". Will proceed to download.'.format(
                file_location
            )
        )
        return True  # update
    logger.debug(f"Current rate file was updated { local_updated }")

    # get the last modified date from the request
    r = cb_request("HEAD", url)
    logger.debug('Checking for available updates at "{}"'.format(url))
    try:
        last_modified = r.headers["Last-Modified"]
        source_updated = datetime.strptime(last_modified, "%a, %d %b %Y %H:%M:%S GMT")
    except KeyError:  # the HTTP header does not contain last-modified date (this is expected for GCE and GCP)
        r = cb_request("GET", url)
        updated_str = r.json().get("updated")
        if updated_str:
            source_updated = datetime.strptime(updated_str, "%d-%B-%Y")
        else:
            logger.debug(
                "Couldn't determine if the source has been updated. Will download file '{}'".format(
                    file_location
                )
            )
            return True  # update

    # check if we need to update the local file.
    logger.debug(f"Source was last modified { source_updated }")
    update = source_updated > local_updated

    if update:
        message = 'Found updates. Will download to "{}"'
    else:
        message = 'Local file is up-to-date with the source. Will not update file "{}"'
    logger.debug(message.format(file_location))

    return update


def download_file(url, directory, file_location):
    """
    Downloads the pricing file for the given json url and saves it to the given directory.
    This is used for AWS, GCE, and GCP file downloads.

    :param url:
    :param directory:
    :param file_location:
    """
    mkdir_p(directory)

    logger.debug(f"Downloading pricing file from { url }")
    r = cb_request("GET", url)
    gp = GlobalPreferences.get()
    if not gp.enable_ssl_verification:
        logger.warning(
            "You currently have the setting 'Enable SSL Verification' disabled. "
            "Therefore, this download will proceed without SSL Verification. "
            "You may change this in Admin > Miscellaneous Settings"
        )
    with open(file_location, "wb") as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
    logger.debug("Download complete")


def split_file(rates_file, products_file, terms_file):
    """
    Splits file into two components for faster lookups.

    :param rates_file: the path to the file containing the rates downloaded from AWS
    :param products_file: contains SKUs for each location/instance type combination.
    :param terms_file: contains the on-demand pricing for each SKU.
    """
    logger.debug("Splitting AWS pricing file")
    extract_json_dict_items(rates_file, products_file, "products")
    extract_json_dict_items(rates_file, terms_file, "terms.OnDemand")
    logger.debug("Split complete")


def extract_json_dict_items(in_path, out_path, key_spec) -> None:
    """
    Extracts a subset of dict items from an existing file to a new file

    :param in_path: full path to a file containing a set of nested JSON objects
    :param out_path: full path to a new file that will contain the extracted items
    :param key_spec: dictionary path identifying the subset of objects to extract
    """
    logger.debug(f"Extracting '{ key_spec }' objects from file { in_path }'")
    # The downloaded AWS rates file grew too large to be read entirely into memory, causing task failures on some test
    # systems. Here, we open the file for streaming, and incrementally parse it, looking for all the direct children of
    # the dictionary path named in the "key_spec". While this is an improvement, there are two potential issues:
    #   1) this code still stores all the requested items in memory before writing any of them out to the file (though
    #      it currently only uses around 10% of the memory needed for the whole rates file)
    #   2) the ijson library does not support two different streaming requests to the same open file, meaning that we
    #      have to open (and parse) it for each subset of data we want to extract.
    with open(in_path, "r") as in_file:
        try:
            items = dict(ijson.kvitems(in_file, key_spec))
        except IncompleteJSONError as exc:
            message = f"Malformed data file. Stored { len(items) } items. Some may be missing."
            logger.warning(message)
            raise exc
    with open(out_path, "w") as out_file:
        json.dump(items, out_file)


def update_servers(resource_tech_name):
    """
    Queries to get all servers which should be updated, then update the rates on each server.

    :param resource_tech_name: The name attribute of the resource technology you wish to update servers for.
    """
    servers = Server.objects.filter(
        resource_handler__resource_technology__name=resource_tech_name
    ).exclude(status="HISTORICAL")

    logger.debug(
        "Will update rates on {} {} servers.".format(
            servers.count(), resource_tech_name
        )
    )
    for server in servers:
        server.save()  # calls self._update_rates()
    logger.debug("Rate Updates complete for {} servers.".format(resource_tech_name))


def run(*args, **kwargs):
    """
    Check for updates on AWS, GCE, and GCP files.
    If updates are needed, downloads and updates rates.

    :param args:
    :param kwargs:
    :return:
    """
    aws_update = check_for_update(aws_file_location, AWS_URL)
    gce_update = check_for_update(gce_file_location, GCE_URL)
    gcp_update = check_for_update(gcp_file_location, GCP_URL)

    if aws_update:
        download_file(AWS_URL, AWS_RATE_HOOK_DIR, aws_file_location)
        products_file = "{}/products_data.json".format(AWS_RATE_HOOK_DIR)
        terms_file = "{}/terms_data.json".format(AWS_RATE_HOOK_DIR)
        split_file(aws_file_location, products_file, terms_file)
        update_servers("Amazon Web Services")

    if gce_update:
        download_file(GCE_URL, GCE_RATE_HOOK_DIR, gce_file_location)
        update_servers("Google Compute Engine")

    if gcp_update:
        download_file(GCP_URL, GCP_RATE_HOOK_DIR, gcp_file_location)
        update_servers("Google Cloud Platform")

    status, output, errors = "SUCCESS", "", ""
    return status, output, errors


if __name__ == "__main__":
    run()
