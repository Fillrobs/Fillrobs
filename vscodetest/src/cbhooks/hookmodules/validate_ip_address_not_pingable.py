from common.methods import is_ip_pingable
from utilities.exceptions import CommandExecutionException  # noqa: F401
from utilities.run_command import run_command  # noqa: F401

"""
Sample hook for validating an IP is not already pingable.
"""


def run(**kwargs):
    ip = kwargs.get("ip")

    pingable = is_ip_pingable(ip)
    if pingable:
        return "FAILURE", "", "pingable: IP already in use"

    return "", "", ""
