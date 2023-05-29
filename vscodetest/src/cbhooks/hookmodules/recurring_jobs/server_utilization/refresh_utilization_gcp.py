from __future__ import print_function

import time  # noqa: F401
from itertools import islice  # noqa: F401

if __name__ == "__main__":
    import django

    django.setup()

from common.methods import set_progress
from resourcehandlers.utilization import GCPSamplingPeriods
from resourcehandlers.gcp.models import GCPHandler


def split_job_into_one_per_resource_handler(parent_job, action):
    rhs = GCPHandler.objects.all()
    rh_count = len(rhs)
    if rh_count == 0:
        return "SUCCESS", "No GCP resource handlers found, nothing to do.", ""

    # The total # of tasks here is wrong - it assumes there are no other actions that will be
    # running for other techs to refresh utilization w/ them. Eventually this will need to be
    # moved to the main refresh utilization job (server_utilization/refresh_all.py).
    set_progress(
        "Refresh Utilization for Servers in {} GCP resource handlers".format(rh_count),
        total_tasks=rh_count + 1,
        tasks_done=1,
    )

    for rh in rhs:
        action.run_as_job(parent_job=parent_job, resource_handler_id=rh.id)

    return parent_job.wait_for_sub_jobs()


def run(job, logger=None, action=None, **kwargs):
    """
    Called by the refresh_server_utilization recurring job

    For all GCP resource handlers, get utilization stats for each active server and save them in
    the related ServerStats model.
    """
    if not action:
        from cbhooks.models import CloudBoltHook

        action = CloudBoltHook.objects.get(name="Refresh Utilization for GCP Servers")

    resource_handler_id = kwargs.get("resource_handler_id", None)
    if not resource_handler_id:
        # spin off jobs for each GCP resource_handler
        return split_job_into_one_per_resource_handler(job, action)

    updated_count = 0
    skipped_count = 0
    metrics = dict(
        last_month=GCPSamplingPeriods.last_month,
        last_week=GCPSamplingPeriods.last_week,
        last_day=GCPSamplingPeriods.last_day,
        last_hour=GCPSamplingPeriods.last_hour,
    )
    total_tasks = 1
    rh = GCPHandler.objects.get(id=resource_handler_id)
    try:
        rh.verify_connection()
    except RuntimeError:
        msg = "Unable to verify connection to handler {}".format(rh)
        logger.exception(msg)
        return "FAILURE", "", msg

    set_progress(tasks_increment=1)

    servers = rh.server_set.exclude(status="HISTORICAL").exclude(
        resource_handler_svr_id=""
    )
    server_count = len(servers)
    total_tasks += server_count
    set_progress(
        "Found {} active servers on RH {}".format(server_count, rh),
        total_tasks=total_tasks,
    )

    utilization = {}
    for metric, period in list(metrics.items()):
        utilization[metric] = get_utilization_for_servers(rh, servers, period)
        set_progress(
            "Retrieved utilization data for the {}".format(metric.replace("_", " "))
        )

    for server in servers:
        server_util = {}
        server_util["last_month"] = utilization["last_month"][server]
        server_util["last_week"] = utilization["last_week"][server]
        server_util["last_day"] = utilization["last_day"][server]
        server_util["last_hour"] = utilization["last_hour"][server]

        stats = server.refresh_stats(server_util)

        if stats:
            updated_count += 1
        else:
            skipped_count += 1
            set_progress(
                'Skipped "{}" because it had no utilization data'.format(server)
            )

        set_progress(tasks_increment=1)

    set_progress(tasks_increment=1)

    output = """
    ServerStats updated: {updated_count}
    Servers skipped: {skipped_count}
    """.format(
        **locals()
    )

    return "SUCCESS", output, ""


def get_utilization_for_servers(rh, servers, period):
    """
    Fetches utilization stats for servers, over the given SamplingPeriod.

    Args
        rh: GCP resource handler instance
        servers: a list of server objects
        period: a SamplingPeriod named tuple with 'samples' and 'interval' integer values.

    Returns utilization data for the given servers over that period.
    """
    utilization_data = {}
    usage_for_vms = rh.get_usage_for_vms(
        servers=servers, interval=period.interval, hours=period.hours,
    )

    # we use enumerate here because GCP sends each server's data back in
    # the same order as the server uuids we sent them

    for count, servers in enumerate(servers):
        utilization_data[servers] = usage_for_vms[count]
    return utilization_data


if __name__ == "__main__":
    """
    For testing, call this directly like so:
        python refresh_utilization_gcp.py
    """
    run(None)
