#!/bin/env python
from builtins import range
import time

from infrastructure.models import Server
from utilities.helpers import cb_request
from utilities.exceptions import NotFoundException
from utilities.logger import ThreadLogger

logger = ThreadLogger(__name__)


def run(logger=None, **kwargs):
    """
    This is the delete_server_from_connector action that is used by Puppet
    Enterprise 2015.3 to remove a node during decommissioning.

    The server being decommissioned must have credentials configured to
    allow CB to run remote scripts on it.
    """
    peconf = kwargs.get("peconf", None)
    if not peconf:
        return (
            "FAILURE",
            "Can't run this action without a puppet enterprise configuration!",
            "",
        )

    # If there is an API connection for the console, use that. Otherwise,
    # default to the master's API connection
    api_conn = peconf.console_api_connection
    if not api_conn:
        api_conn = peconf.master_api_connection
        if not api_conn:
            msg = "There must be either a Console or Master API Connection object associated with the PE Configuration!"
            return "FAILURE", msg, ""

    server = kwargs.get("server")
    try:
        assert isinstance(server, Server)
    except AssertionError:
        logger.info(
            "Expected Server instance, got {} instead!".format(
                server.__class__.__name__
            )
        )
        raise
    server_username = server.get_credentials().get("username")
    server_password = server.get_credentials().get("password")
    server_key = server.get_credentials().get("keyfile")
    if not server_username or (not server_password and not server_key):
        msg = (
            "The server being deleted must have a username & either "
            "a password or SSH key associated with it to use for running remote scripts."
        )
        return "FAILURE", msg, ""

    cert_name = get_server_certname(server, logger)

    # Stop the node's Puppet Agent
    # If we don't do this, the node might check in while we're in the middle of getting rid of it.
    if server.os_family.name.upper() == "WINDOWS":
        server.execute_script(script_contents="stop-service puppet")
    else:
        server.execute_script(script_contents="service puppet stop")
        server.execute_script(script_contents="chkconfig puppet off")

    # UNPIN THE NODE FROM THE GROUPS ASSOCIATED WITH THE NODE THROUGH CB APPLICATIONS
    # TODO: Move the following code to the remove_node_from_all_groups feature
    logger.info("Unpinning the node from groups")

    api_base_url = "{}://{}:{}".format(api_conn.protocol, api_conn.ip, api_conn.port)
    pe_usertoken = get_puppet_api_rbac_token(
        api_conn.username, api_conn.password, api_base_url, logger
    )

    for app in server.applications.all():
        # Get the Existing Group Object
        peg = app.pegroup_set.get(pe_conf_id=peconf.id)
        url = "{}/classifier-api/v1/groups/{}".format(api_base_url, peg.uuid)
        headers = {"X-Authentication": pe_usertoken}
        r = cb_request("GET", url, headers=headers)
        logger.debug("Response code for getting group object: {}".format(r.status_code))
        group_details = r.json()
        logger.debug("Group details from API: {}".format(group_details))

        # Remove the Node from the Group's Rules
        # The rule syntax is defined here: https://docs.puppetlabs.com/pe/latest/nc_groups.html#rule-condition-grammar
        rules = group_details.get("rule")
        if rules:
            # The initial boolean is not a list; keep it
            # For the subsequent lists, only keep those where the 3rd item (value to
            # compare) is not the name of this node's cert
            rules = [r for r in rules if not isinstance(r, list) or r[2] != cert_name]
            # If after removing this node there's only one item, it's the initial
            # boolean operator only, so just set rules to None
            if len(rules) == 1:
                rules = None
        group_details["rule"] = rules

        # Update the Group in Puppet
        headers["Content-Type"] = "application/json"
        r = cb_request("POST", url, headers=headers, json=group_details)
        logger.debug(
            "Response code for POSTing modified group: {}".format(r.status_code)
        )

    # Clean/revoke the certificate with puppet master
    peconf.clean_cert(cert_name)

    if server.pe_node:
        server.pe_node.delete()

    return "", "", ""


def get_server_certname(server, logger):
    # Wait for Node to Request Certificate & Get Cert Name
    logger.info("Getting cert name from server.")
    cert_name = ""

    while cert_name == "":
        if server.os_family.name.upper() == "WINDOWS":
            try:
                cert_name = server.execute_script(
                    script_contents="facter networking.fqdn"
                )
            except NotFoundException:
                logger.info("The vm {} could not be found.".format(cert_name))
                return cert_name

        else:
            try:
                cert_name = server.execute_script(
                    script_contents="/usr/local/bin/facter networking.fqdn"
                )
            except NotFoundException:
                logger.info("The vm {} could not be found.".format(cert_name))
                return cert_name
        time.sleep(5)
    # The cert name from facter may have capital letters, but the Puppet Master
    # is all lowercase so match that
    return cert_name.lower()


def get_puppet_api_rbac_token(uid, pwd, api_base_url, logger):
    # Get an RBAC API Token
    url = "{}/rbac-api/v1/auth/token".format(api_base_url)
    headers = {"Content-Type": "application/json"}
    auth_data = {"login": uid, "password": pwd}
    r = cb_request("POST", url, headers=headers, json=auth_data)
    logger.debug("Response code for token request: {}".format(r.status_code))
    if r.status_code not in list(range(200, 300)):
        msg = (
            "Unable to get API Token from PE. Check your PE Console or Master API "
            "Connection as invalid credentials are one possible cause.\n"
            "Response code: {}\nFull response: {}".format(r.status_code, r.json())
        )
        return "FAILURE", msg, ""
    # Returns JSON that contains 'token' key, need value of that key
    return r.json().get("token")
