from __future__ import division


def get_cpu_utilization(servers):
    """
    This method is a sample of how CPU utilization can be checked against VMware
    gathered statistics. This could be changed to gather stats from a monitoring system,
    or even running remote scripts on servers to fetch their load averages.

    For more on VMware CPU performance counters see
    https://www.vmware.com/support/developer/vc-sdk/visdk41pubs/ApiReference/cpu_counters.html

    This action makes the assumption that all servers belong to the same VSphereResourceHandler

    :param servers: servers whose CPU stats should be fetched
    :return: an average CPU utilization on those servers, represented as a number between 0 and 100
    """
    cpu_averages_aggregate = 0.0
    vmware = servers.first().resource_handler.cast()

    # call the abstraction used by CB to return server stats
    # defaults to '300' (5 minutes sampling period and 288 datapoints
    # For more on PerfIntervals:
    # https://www.vmware.com/support/developer/vc-sdk/visdk41pubs/ApiReference/vim.HistoricalInterval.html
    usage_stats = vmware.get_usage_for_vms(servers, "300", "288")

    # sum all the values for servers that have been used
    # we can skip servers that haven't been used since a usage of 0 is accurate
    cpu_averages_aggregate = sum(
        [
            usage_stat.get("cpu_usage_average", 0)
            for usage_stat in usage_stats
            if usage_stat
        ]
    )

    return cpu_averages_aggregate / len(servers)
