"""
Calculates the on-demand rate for the chosen AWS instance type.

Rate is displayed in the time units chosen in Rates Options. Assumes the
currency is USD, edit this action to change it.

This file is applied when provisioning a server.
These rates are updated regularly by the 'Refresh Server Rates' recurring job.
"""


from decimal import Decimal
import os.path  # noqa: F401
import json

from multiprocessing import Process, Queue  # noqa: F401

import boto3
from django.conf import settings  # noqa: F401
from django.core.cache import cache
from pkg_resources import resource_filename  # noqa: F401

from costs.utils import default_compute_rate
from resourcehandlers.aws.aws_wrapper import get_region_title
from resourcehandlers.aws.models import AWSHandler
from utilities.filesystem import mkdir_p  # noqa: F401
from utilities.logger import ThreadLogger
from utilities.models import GlobalPreferences
from utilities.helpers import cb_request  # noqa: F401


NUMBER_OF_HOURS = {
    "HOUR": 1,
    "DAY": 24,
    "WEEK": 192,
    "MONTH": 720,  # assumes 30-day month
    "YEAR": 8760,  # assumes 365-day year
}

logger = ThreadLogger(__name__)


def _compute_aws_rate(region, os_build, instance_type, environment):
    resource_handler: AWSHandler = environment.resource_handler.cast()
    wrapper = resource_handler.get_api_wrapper()

    resource_technology = environment.get_resource_technology()
    if getattr(resource_technology, "slug", "") == "aws_govcloud":
        account = resource_handler.billingaccount
        passwd = resource_handler.billingpasswd
    else:
        account = resource_handler.serviceaccount
        passwd = resource_handler.servicepasswd

    boto3_args = wrapper.get_boto3_args("us-east-1", account, passwd)

    pricing_client = boto3.client("pricing", **boto3_args)

    filters = [
        {"Type": "TERM_MATCH", "Field": "tenancy", "Value": "shared"},
        {"Type": "TERM_MATCH", "Field": "operatingSystem", "Value": os_build},
        {"Type": "TERM_MATCH", "Field": "preInstalledSw", "Value": "NA"},
        {"Type": "TERM_MATCH", "Field": "instanceType", "Value": instance_type},
        {"Type": "TERM_MATCH", "Field": "location", "Value": region},
        {"Type": "TERM_MATCH", "Field": "capacitystatus", "Value": "Used"},
    ]
    data = pricing_client.get_products(ServiceCode="AmazonEC2", Filters=filters)

    try:
        on_demand_price_list = json.loads(data["PriceList"][0])["terms"]["OnDemand"]
        logger.debug(f"AWS pricing information found using these filters: {filters}")
    except IndexError:
        logger.debug(f"No AWS pricing information found using these filters: {filters}")
        return None

    price_list = list(on_demand_price_list)[0]
    price_dimension = list(on_demand_price_list[price_list]["priceDimensions"])[0]
    return on_demand_price_list[price_list]["priceDimensions"][price_dimension][
        "pricePerUnit"
    ]["USD"]


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
        # This is also useful for testing to check whether we returned rates just from AWS.
        logger.info("Only including AWS-specific rates from the AWS rate hook.")
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
        # rate from AWS.
        rate_dict.update({"Hardware": {}})
        logger.info("Including the default Admin/rates in the AWS rate hook.")

    server = kwargs.get("server", None)
    # If being called from a context where we have a server object that stores
    # AWS-specific info, reference that first for the instance type
    instance_type = None
    region_name = None

    if server and hasattr(server, "ec2serverinfo") and server.ec2serverinfo:
        instance_type = server.ec2serverinfo.instance_type
        region_name = server.ec2serverinfo.ec2_region

    if not instance_type:
        for cfv in cfvs:
            if cfv.field.name == "instance_type" and cfv.value:
                instance_type = cfv.value
                break

    if not instance_type:
        # Perhaps the instance_type is in a preconfiguration.
        for pcvs in pcvss:
            instance_type_cfvs = pcvs.custom_field_values.filter(
                field__name="instance_type"
            )
            if instance_type_cfvs.count() > 0:
                # Let's just take the first instance_type returned if we get more than 1.
                instance_type = instance_type_cfvs[0].value
                break

    if not instance_type:
        logger.warning("Could not determine instance type, unable to calculate rate")
        return rate_dict

    if not region_name:
        rh = AWSHandler.objects.first()
        region_name = rh.get_env_region(environment)

    if not region_name:
        logger.warning("Could not determine region, unable to calculate rate.")
        return rate_dict

    # Locations are full titles, like "US West (N. California)"
    location = get_region_title(region_name)

    cache_key = "{}:{}".format(region_name, instance_type)
    rate = cache.get(cache_key)

    if rate:
        logger.debug(
            "Using cached rate {} for {} type in {}".format(
                rate, instance_type, location
            )
        )
    else:
        os_base_name = ""
        if not os_build:
            if server.os_family:
                if server.os_family.name in ["RHEL", "SUSE"]:
                    os_base_name = server.os_family.name
                else:
                    os_base_name = server.os_family.get_base_name()
        else:
            if os_build.os_family:
                os_base_name = os_build.os_family.get_base_name()

        if os_base_name == "":
            logger.warning("Could not determine OS family, unable to calculate rate.")
            return rate_dict
        rate = _compute_aws_rate(location, os_base_name, instance_type, environment)
        if rate is None:
            return rate_dict

        cache.set(cache_key, rate)

    rate_time_unit = GlobalPreferences.objects.get().rate_time_unit
    number_of_hours = NUMBER_OF_HOURS.get(rate_time_unit, 0)
    rate_dict.update(
        {"Hardware": {"Instance Type": Decimal(rate) * number_of_hours * quantity}}
    )

    return rate_dict
