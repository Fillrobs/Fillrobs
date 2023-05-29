"""
Called by the Refresh All Server Utilization recurring job.
"""


if __name__ == "__main__":
    import django

    django.setup()


from common.methods import set_progress
from resourcehandlers.azure_arm.models import AzureARMHandler
from resourcehandlers.utilization import AzureARMSamplingPeriods


def split_job_into_one_per_resource_handler(parent_job, action):
    rhs = AzureARMHandler.objects.all()
    rh_count = len(rhs)
    if rh_count == 0:
        return "SUCCESS", "No Azure ARM resource handlers found, nothing to do.", ""

    set_progress(
        "Refresh Utilization for Servers in {} Azure ARM resource handlers".format(
            rh_count
        ),
        total_tasks=rh_count + 1,
        tasks_done=1,
    )

    for rh in rhs:
        action.run_as_job(parent_job=parent_job, resource_handler_id=rh.id)

    return parent_job.wait_for_sub_jobs()


def run(job, logger=None, action=None, **kwargs):
    """
    For all Azure ARM resource handlers, get utilization stats for each active server and save them in
    the related ServerStats model.
    """
    if not action:
        from cbhooks.models import CloudBoltHook

        action = CloudBoltHook.objects.get(
            name="Refresh Utilization for Azure ARM Servers"
        )

    resource_handler_id = kwargs.get("resource_handler_id", None)
    if not resource_handler_id:
        # spin off jobs for each Azure ARM resource_handler
        return split_job_into_one_per_resource_handler(job, action)

    updated_count = 0
    skipped_count = 0
    metrics = dict(
        last_month=AzureARMSamplingPeriods.last_month,
        last_week=AzureARMSamplingPeriods.last_week,
        last_day=AzureARMSamplingPeriods.last_day,
        last_hour=AzureARMSamplingPeriods.last_hour,
    )
    total_tasks = 1
    rh = AzureARMHandler.objects.get(id=resource_handler_id)
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

    uuids = [server.resource_handler_svr_id for server in servers]

    utilization = {}
    for metric, period in list(metrics.items()):
        utilization[metric] = get_utilization_for_servers(rh, uuids, period)
        set_progress(
            "Retrieved utilization data for the {}".format(metric.replace("_", " "))
        )

    for server in servers:
        server_util = {}
        server_util["last_month"] = utilization["last_month"][
            server.resource_handler_svr_id
        ]
        server_util["last_week"] = utilization["last_week"][
            server.resource_handler_svr_id
        ]
        server_util["last_day"] = utilization["last_day"][
            server.resource_handler_svr_id
        ]
        server_util["last_hour"] = utilization["last_hour"][
            server.resource_handler_svr_id
        ]

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


def get_utilization_for_servers(rh, uuids, period):
    """
    Fetches utilization stats for servers, over the given SamplingPeriod.

    Args
        rh: Azure resource handler instance
        uuids: a list of server uuids (resource_handler_svr_id)
        period: a SamplingPeriod named tuple with 'interval' and 'hours' integer values.

    Returns utilization data for the given servers over that period.
    """
    utilization_data = {}
    usage_for_vms = rh.get_usage_for_vms(
        uuids=uuids, interval=period.interval, hours=period.hours
    )

    # we use enumerate here because our implementation of get_usage_for_vms for Azure ARM
    # returns these servers in the same order we sent them
    for count, uuid in enumerate(uuids):
        utilization_data[uuid] = usage_for_vms[count]
    return utilization_data


if __name__ == "__main__":
    """
    For testing, call this directly like so:
        python refresh_utilization_azure.py
    """
    run(None)
