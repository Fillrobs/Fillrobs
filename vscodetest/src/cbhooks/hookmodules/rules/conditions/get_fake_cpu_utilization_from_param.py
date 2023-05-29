import os  # noqa: F401

from settings import VARDIR  # noqa: F401

from common.methods import set_progress  # noqa: F401


def get_cpu_utilization(servers):
    """
    This method reads the value of the parameter named "simulated_cpu_load" from the
    resource and returns it.

    This is useful for simulating scale up/down conditions to ensure scaling works as expected (
    without having to add/remove real load from those servers). This can be modified from the CB
    UI on the parameters tab for a resource.
    """
    resource = servers[0].resource
    cpu_load_cfv = resource.get_cfv_for_custom_field("simulated_cpu_load")
    if cpu_load_cfv:
        return cpu_load_cfv.value
    return None
