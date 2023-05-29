"""
Download last month's billing data for the public cloud providers and add any server-related costs
to the CB DB.
"""
import calendar
import datetime
import os
import zipfile
import pandas
from django.core.exceptions import MultipleObjectsReturned
from pandas import Grouper
import re

from common.methods import set_progress
from costs.models import BillingSummary
from infrastructure.models import Server
from resourcehandlers.models import ResourceHandler
from utilities.logger import ThreadLogger

logger = ThreadLogger(__name__)


def import_row(row, svr):
    """
    Create an AWSBillingLineItem for a single row. Avoid duplicate rows for servers and dates as the two fields
    that should be unique together. Update the rest.
    """
    reserved_instance_mapping = {"Y": True, "N": False}

    from resourcehandlers.aws.models import AWSBillingLineItem

    AWSBillingLineItem.objects.update_or_create(
        date=row["UsageStartDate"],
        server=svr,
        defaults=dict(
            quantity=row["UsageQuantity"],
            rate=row["BlendedRate"],
            cost=row["BlendedCost"],
            reserved_instance=reserved_instance_mapping.get(
                row["ReservedInstance"], False
            ),
        ),
    )


def import_summary_row(index, row, rh, start_datetime, end_datetime, column=None):
    """
    Create or update an instance of BillingSummary for the grouped data.
    :param row:
    :param column:
    :return:
    """
    BillingSummary.objects.update_or_create(
        start_date=start_datetime,
        end_date=end_datetime,
        column=column,
        category=index,
        resource_handler=rh,
        defaults=dict(
            quantity=row["UsageQuantity"],
            rate=row["BlendedRate"],
            cost=row["BlendedCost"],
        ),
    )


def import_csv_billing_data(
    rh,
    csv_filename,
    already_imported_servers_data,
    already_imported_summary_data,
    bill_month,
    bill_year,
):
    """
    Convert the CSV to a pandas dataFrame and then import data for servers and billing summaries.
    """
    # Initialize a pandas dataframe with only the needed columns
    columns = [
        "ProductName",
        "UsageType",
        "UsageStartDate",
        "UsageEndDate",
        "UsageQuantity",
        "ResourceId",
        "ReservedInstance",
    ]

    rate_columns = ["BlendedRate", "BlendedCost"]

    try:
        df = pandas.read_csv(csv_filename, usecols=columns + rate_columns)
    except ValueError:
        try:
            # AWS used these other column names in older billing exports
            df = pandas.read_csv(csv_filename, usecols=columns + ["Rate", "Cost"])
            # Now just rename the columns to normalize the data for processing.
            df = df.rename(
                index=str, columns={"Rate": "BlendedRate", "Cost": "BlendedCost"}
            )
        except ValueError:
            logger.info(
                f"The file {csv_filename} does not contain necessary information for billing. Skipping..."
            )
            # We are processing a file that does not contain the needed columns, so continue on to the next file.
            return

    if not already_imported_servers_data:
        import_servers_billing_data(df, rh, csv_filename)
    if not already_imported_summary_data:
        # This is important to avoid creating duplicate entries.
        import_summary_data(df, rh, csv_filename, bill_month, bill_year)


def import_servers_billing_data(df, rh, csv_filename):
    """
    Cut down the dataFrame to EC2 costs that relate to a Server in CB,
    and if so, import each row of data for that server.
    """
    # Only process EC2 charges that we can relate to Server records for now
    instances_in_cb = Server.objects.filter(resource_handler=rh).values_list(
        "resource_handler_svr_id", flat=True
    )

    servers_df = df.where(
        (df["ProductName"] == "Amazon Elastic Compute Cloud")
        & (
            df["ResourceId"].isin(instances_in_cb)
        )  # Instance IDs always start with this.
    ).dropna()

    if len(servers_df) == 0:
        logger.info(
            f"There was no data found for EC2 instances in CloudBolt, "
            f"so no data will be saved from file {csv_filename}."
        )
        return
    else:
        logger.info(
            f"Will import {len(servers_df)} rows of data relevant to EC2 instances in CloudBolt"
        )

    # Convert UsageStartDate column to datetime to allow resampling by time range.
    servers_df["UsageStartDate"] = servers_df["UsageStartDate"].apply(
        pandas.to_datetime, format="%Y-%m-%d %H:%M:%S"
    )

    # Aggregate hourly data to daily so that we have fewer instances of billing data to save to the database.
    servers_df = (
        servers_df.groupby(
            ["ResourceId", "ReservedInstance", Grouper(key="UsageStartDate", freq="D")]
        )
        .agg({"UsageQuantity": "sum", "BlendedCost": "sum", "BlendedRate": "mean"})
        .reset_index()
    )

    # Group by servers to easily access per-server data
    server_groupby = servers_df.groupby(["ResourceId"])

    # Only iterate over rows for servers that are already discovered by CB
    for resource_id in instances_in_cb:
        try:
            data = server_groupby.get_group(resource_id)
            svr = Server.objects.get(
                resource_handler=rh, resource_handler_svr_id=resource_id
            )
            set_progress(
                f"Will save billing data for AWS instance '{svr.hostname}' with id '{resource_id}'"
            )
            for index, row in data.iterrows():
                import_row(row, svr)
        except KeyError:
            logger.info(f"No billing data found for instance with ID '{resource_id}'.")
        except MultipleObjectsReturned:
            logger.info(
                f"Skipping '{resource_id}.' More than one Server object returned."
            )


def import_summary_data(df, rh, csv_filename, bill_month, bill_year):
    """
    Group data by category and summarize the data for the month, save to BillingSummary for the RH.
    """
    set_progress(
        f"Importing summarized billing data for billing month {bill_month}-{bill_year}"
    )

    # Determine the start and end date for the billing cycle (assume it was the first to last day of the month)
    end_day = calendar.monthrange(bill_year, bill_month)[1]
    start_day = 1

    start_datetime = datetime.datetime(bill_year, bill_month, start_day, 0, 0, 0)
    end_datetime = datetime.datetime(bill_year, bill_month, end_day, 23, 59, 59)

    summary_kwargs = {
        "UsageQuantity": "sum",
        "BlendedCost": "sum",
        "BlendedRate": "mean",
    }

    columns_to_summarize = ["ProductName", "UsageType", "ReservedInstance"]

    for col in columns_to_summarize:
        summary_df = df.groupby(col).agg(summary_kwargs).dropna()

        for index, row in summary_df.iterrows():
            import_summary_row(index, row, rh, start_datetime, end_datetime, column=col)


def download_and_extract(bucket, filename, rh_dir):
    """
    Download the specified filename from the given bucket into rh_dir. This file is assumed to
    be a zip, and the first .csv file is extracted from the zip. The zip is deleted and the full
    path to the .csv is returned.
    """
    local_zipfilename = os.path.join(rh_dir, filename)
    set_progress(f"Downloading file {filename} to {local_zipfilename}.")
    bucket.download_file(filename, local_zipfilename)
    zip_file = zipfile.ZipFile(local_zipfilename)
    for name in zip_file.namelist():
        if name.endswith(".csv"):
            logger.info(f"Extracting {name} from {filename}")
            zip_file.extract(name, path=rh_dir)
            break
    os.unlink(local_zipfilename)
    return os.path.join(rh_dir, name)


def parse_bill_date(filename):
    """
    Uses regex to extract the year and month of the given billing file, for which AWS has a naming standard
    which we can reasonably assume will always contain the year and month as 'YYYY-MM' at the end of the file's name.
    """
    pattern = re.compile(
        r"[0-9]{4}-[0-9]{2}"
    )  # Match the date, i.e. '2018-12' in the filename
    match = re.search(pattern, filename)
    if match:
        bill_year, bill_month = (int(i) for i in match.group(0).split("-"))
        return bill_year, bill_month
    else:
        return None, None


def run(job, *args, **kwargs):
    """
    For each resource handler that supports it, import the billing data.
    """
    status = "SUCCESS"
    for rh in ResourceHandler.objects.all():
        rh = rh.cast()
        if not rh.can_get_billing_data:
            continue
        set_progress(f"Processing {rh}.")
        try:
            rh.import_billing_data()
        except Exception as err:
            # Log the failure and continue to try to process the other RHs
            msg = f"Failed to get billing data for {rh}: {err}"
            set_progress(msg)
            logger.exception(msg)
            status = "FAILURE"

    return status, "", ""
