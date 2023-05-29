import os

from settings import VARDIR

from common.methods import set_progress  # noqa: F401


def get_cpu_utilization(servers):
    """
    This method is a sample of how CPU utilization can be checked by creating the file
    /var/opt/cloudbolt/cpu_usage with just an integer in it.  This is useful for
    easily simulating scale up/down conditions to ensure scaling works as expected (without
    having to add/remove real load from those servers).
    """
    cpu_usage_filepath = os.path.join(VARDIR, "opt", "cloudbolt", "cpu_usage")
    if os.path.isfile(cpu_usage_filepath):
        # set_progress("      Found cpu_usage file {}, using that.".format(cpu_usage_filepath))
        f = open(cpu_usage_filepath)
        return int(f.read())
    return None
