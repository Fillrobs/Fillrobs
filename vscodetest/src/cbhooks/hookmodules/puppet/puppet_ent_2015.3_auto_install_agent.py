from builtins import range
import re
import time
from cbhooks.models import CloudBoltHook

from common.methods import set_progress
from utilities.helpers import cb_request


IS_AUTOSIGN_ENABLED_ON_PEMASTER = bool("{{ is_autosign_enabled_on_pemaster }}")
WINDOWS_AGENT_URL = (
    "https://downloads.puppetlabs.com/windows/puppet-agent-1.4.2-x64.msi"
)


def run(job, logger=None, **kwargs):
    """
    This is the auto_install_agent action that is used by Puppet Enterprise
    2015.3 to boostrap a puppet agent onto the node being provisioned and do
    some initial setup. Namely, after bootstrapping the agent it adds the node
    to groups based on applications chosen, and runs the puppet agent to apply
    those changes.

    The server being provisioned must have credentials configured to
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
            msg = (
                "There must be either a Console or Master API Connection "
                "object associated with the PE Configuration!"
            )
            return "FAILURE", msg, ""

    # prov jobs only ever have 1 server, so we'll take the first one
    server = job.server_set.first()
    server_username = server.get_credentials().get("username")
    server_password = server.get_credentials().get("password")
    server_key = server.get_credentials().get("keyfile")
    if not server_username or (not server_password and not server_key):
        msg = (
            "The server being provisioned must have a username & either "
            "a password or SSH key associated with it to use for running "
            "remote scripts."
        )
        set_progress(msg)
        return "FAILURE", msg, ""

    # BOOTSTRAP THE NODE'S AGENT & HANDLE CERTS

    if server.os_family.name.upper() == "WINDOWS":
        bootstrap_windows_server(server, peconf, logger)
    else:
        bootstrap_linux_server(server, peconf, logger)

    cert_name = get_server_certname(server, logger)

    # ADD THE NODE TO THE GROUPS TIED TO SELECTED APPLICATIONS
    logger.info("Adding the node to groups")
    api_base_url = "{}://{}:{}".format(api_conn.protocol, api_conn.ip, api_conn.port)
    pe_usertoken = get_puppet_api_rbac_token(
        api_conn.username, api_conn.password, api_base_url, logger
    )
    apps = kwargs.get("apps", [])
    for app in apps:
        # Get the Existing Group Object
        peg = app.pegroup_set.get(pe_conf_id=peconf.id)
        url = "{}/classifier-api/v1/groups/{}".format(api_base_url, peg.uuid)
        headers = {"X-Authentication": pe_usertoken}
        r = cb_request("GET", url, headers=headers)
        logger.debug("Response code for getting group object: {}".format(r.status_code))
        group_details = r.json()
        logger.debug("Group details from API: {}".format(group_details))
        if r.status_code != 200:
            msg = "Failed to retrieve node group {}".format(app.name)
            return "FAILURE", msg, "Details: {}".format(group_details)

        # Append the Node to the Group's Rules
        # The rule syntax is defined here:
        #    https://docs.puppetlabs.com/pe/latest/nc_groups.html#rule-condition-grammar
        # Assumption: noone else is messing with rules, so it always starts with ‘or’
        new_rule = ["=", "name", "{}".format(cert_name)]
        rules = group_details.get("rule")
        # If there are no rules, just set it to the new one; otherwise, append
        if rules:
            rules = rules + [new_rule]
        else:
            rules = ["or", new_rule]
        group_details["rule"] = rules

        # Assign Node to Requested Groups
        headers["Content-Type"] = "application/json"
        r = cb_request("POST", url, headers=headers, json=group_details)
        logger.debug(
            "Response code for POSTing modified group: {}".format(r.status_code)
        )
        if r.status_code != 200:
            try:
                post_details = r.json()
            except ValueError:
                post_details = "No JSON returned."
            msg = "Failed to add node {} to group {}".format(server.hostname, app.name)
            return (
                "FAILURE",
                msg,
                "POST failed with status {} and details: "
                "{}".format(r.status_code, post_details),
            )

    if not IS_AUTOSIGN_ENABLED_ON_PEMASTER:
        # Start child job loop to sign the certificate
        action_sign_cert = CloudBoltHook.objects.get(name="puppet_ent_2015.3_sign_cert")
        action_sign_cert.run_as_job(
            server=server,
            owner=job.owner,
            parent_job=job,
            peconf=peconf,
            peconf_id=peconf.id,
            pe_usertoken=pe_usertoken,
            cert_name=cert_name,
        )

    # RUN PUPPET ON THE NODE
    logger.info("Running puppet on the new server")
    # Sync Node Until No More Work to Do
    agent_result = ""
    return_code = "1"
    # The puppet agent returns 2 if it's a success but there's more work to do,
    # 0 for success with no more work to do, and other for failure
    # But sometimes it gives an erroneous "bad" return code early on, so retry
    num_retries = 10
    p = re.compile(r"RETURNCODEFORCB=(?P<code>[0-9]*)")
    while return_code not in ["0", "2"] and num_retries > 0:
        agent_result = get_agent_result(server)
        m = p.search(agent_result)
        return_code = m.group("code")
        logger.debug("Return code: {}".format(return_code))
        logger.debug("May retry up to {} more times if necessary".format(num_retries))
        time.sleep(5)
        num_retries -= 1
    if return_code not in ["0", "2"]:
        return (
            "FAILURE",
            "Error running puppet agent on node",
            "Result: {}".format(agent_result),
        )

    # Synchronize server with CloudBolt
    peconf.sync_servers()

    return "", "", ""


def bootstrap_windows_server(server, peconf, logger):
    logger.info("Bootstrapping the Windows agent")
    script = """
    mkdir c:\\temp
    $wc = New-Object System.Net.WebClient
    $wc.DownloadFile("{0}", "c:\\temp\puppet-agent.msi")
    Start-Process msiexec -ArgumentList "/qn /norestart /i C:\\temp\puppet-agent.msi PUPPET_MASTER_SERVER={1}" -Wait -Passthru
    """  # noqa: W605
    script = script.format(WINDOWS_AGENT_URL, peconf.hostname)
    server.execute_script(script_contents=script)


def bootstrap_linux_server(server, peconf, logger):
    logger.info("Bootstrapping the Linux agent")
    script = (
        "curl -k https://{0}:8140/packages/current/install.bash"
        "| bash -s main:server={0}"
    ).format(peconf.hostname)
    server.execute_script(script_contents=script, timeout=600)


def get_server_certname(server, logger):
    nic = server.nics.first()
    domain = nic.network.dns_domain
    if domain is not None:
        cert_name = server.hostname + "." + domain
    else:
        msg = """The server being provisioned must have a network DNS domain
        configured to request a certificate from the Puppet Master."""
        set_progress(msg)
    return cert_name.lower().rstrip()


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


def get_agent_result(server):
    if server.os_family.name.upper() == "WINDOWS":
        agent_result = server.execute_script(
            script_contents="puppet agent -t; echo RETURNCODEFORCB=$lastexitcode",
            timeout=600,
        )
    else:
        agent_result = server.execute_script(
            script_contents="/usr/local/bin/puppet agent -t; echo RETURNCODEFORCB=$?"
        )

    return agent_result
