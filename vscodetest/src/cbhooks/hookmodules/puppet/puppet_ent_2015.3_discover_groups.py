from builtins import range

from connectors.puppet_ent.models import PEGroup
from utilities.exceptions import CloudBoltException

from utilities.helpers import cb_request
from utilities.logger import ThreadLogger

logger = ThreadLogger(__name__)


def discover_groups(**kwargs):
    """
    This is the discover_groups action that is used by Puppet
    Enterprise 2015.3 to determine which groups are available in PE and make
    PEGroup objects for them. Used to import groups.
    """

    peconf = kwargs.get("peconf", None)
    if not peconf:
        raise CloudBoltException(
            "Can't run this action without a puppet enterprise configuration!"
        )

    # If there is an API connection for the console, use that. Otherwise,
    # default to the master's API connection
    api_conn = peconf.console_api_connection
    if not api_conn:
        api_conn = peconf.master_api_connection
        if not api_conn:
            msg = "There must be either a Console or Master API Connection object associated with the PE Configuration!"
            raise CloudBoltException(msg)

    api_base_url = "{}://{}:{}".format(api_conn.protocol, api_conn.ip, api_conn.port)
    # Get an RBAC API Token
    url = "{}/rbac-api/v1/auth/token".format(api_base_url)
    headers = {"Content-Type": "application/json"}
    auth_data = {"login": str(api_conn.username), "password": api_conn.password}
    r = cb_request("POST", url, headers=headers, json=auth_data)

    logger.debug("Response code for token request: {}".format(r.status_code))
    if r.status_code not in list(range(200, 300)):
        msg = (
            "Unable to get API Token from PE. Check your PE Console or Master API "
            "Connection as invalid credentials are one possible cause.\n"
            "Response code: {}\nFull response: {}".format(r.status_code, r.json())
        )
        raise CloudBoltException(msg)
    # Returns JSON that contains 'token' key, need value of that key
    pe_usertoken = r.json().get("token")

    # Get the groups from the API
    headers["X-Authentication"] = pe_usertoken
    url = "{}/classifier-api/v1/groups".format(api_base_url)
    r = cb_request("GET", url, headers=headers)
    groups = []

    ignored_groups = ["default", "PE.*"]
    logger.debug("Response for API call for groups: {}".format(r.json()))
    group_reps = [g for g in r.json() if g["name"] not in ignored_groups]
    for g in group_reps:
        group = PEGroup(name=g["name"], uuid=g["id"], pe_conf=peconf)
        groups.append(group)

    return groups
