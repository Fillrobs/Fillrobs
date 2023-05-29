from utilities.exceptions import CommandExecutionException
from utilities.run_command import run_command

"""
Sample hook for validating an IP using nslookup.
"""


def run(**kwargs):
    ip = kwargs.get("ip")
    hostname = kwargs.get("hostname")

    try:
        output = run_command("nslookup {}".format(ip))

        if hostname and hostname not in output:
            return "FAILURE", output, "nslookup: IP already in use"

    except CommandExecutionException as e:
        if e.rv == 1:
            if "can't find " in e.output:
                # did not know this IP, we'll assume it's OK
                return "", "", ""

        # any other execution exception should be treated as a failure
        return "FAILURE", e.output, str(e)

    return "", "", ""
