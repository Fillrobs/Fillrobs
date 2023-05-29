import json

from connectors.puppet_ent.puppet_ent_api import PuppetRequest
from utilities.exceptions import CloudBoltException
from utilities.helpers import cb_request
from utilities.logger import ThreadLogger
from common.methods import set_progress

logger = ThreadLogger(__name__)


def get_groups(api_base_url, pe_usertoken):
    """
    Get a list of classification groups in the PE console
    """
    url = "{}/classifier-api/v1/groups".format(api_base_url)
    headers = {"X-Authentication": pe_usertoken}
    r = cb_request("GET", url, headers=headers)
    return r.json()


def check_fetch_sign_cert(peconf):
    """
    A certificate request (CSR) is generated when a new PE connector is created in CB
    The certificate must be manually signed as CB does not yet have access to to sign
    certificates via the API.
    This should be a button in the connector UI page
    """
    if not peconf.ssl_signed_cert:
        msg = "Fetching Puppet Certificate: {}".format(peconf.cert_name)
        set_progress(msg)
        peconf.fetch_signed_cert()
    if peconf.ssl_signed_cert:
        return True
    else:
        return False


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


def add_to_ca_whitelist(api_base_url, pe_usertoken, group_ca_id, peconf):
    """
    https://puppet.com/docs/puppet/5.4/http_api/http_certificate_status.html
    https://puppet.com/docs/puppet/5.4/schemas/host.json
    Remote API access is to 'puppet-ca' '/certificate_status/' is only capable with a whitelisted-certificate
    This is a dependency run-once method using token auth to set the generated certname in the whitelist
    Puppet Ent provides modules with parameters to properly setup the whitelist
    A puppet run is required on the master to complete this configuration
    """

    pe_cert_name = peconf.cert_name
    url = "{}/classifier-api/v1/groups/{}".format(api_base_url, group_ca_id)
    headers = {"X-Authentication": pe_usertoken}
    r = cb_request("GET", url, headers=headers)
    group_details = r.json()
    # Sets using config_data as using a class param causes puppet master runs to fail
    if "config_data" not in group_details:
        logger.info(
            "Add cloudbolt certificate to puppet_enterprise::profile::certificate_authority::client_whitelist using hiera"
        )
        logger.info(
            "For example on the puppetmaster: echo -e '\\n\\npuppet_enterprise::profile::certificate_authority::client_whitelist:\\n - '{}'\\n' >> /etc/puppetlabs/code/environments/production/data/common.yaml".format(
                pe_cert_name
            )
        )
        return

    if (
        "puppet_enterprise::profile::certificate_authority"
        not in group_details["config_data"]
    ):
        group_details["config_data"][
            "puppet_enterprise::profile::certificate_authority"
        ] = {"client_whitelist": [pe_cert_name]}
    else:
        group_details["config_data"][
            "puppet_enterprise::profile::certificate_authority"
        ].setdefault("client_whitelist", [])
        if (
            pe_cert_name
            not in group_details["config_data"][
                "puppet_enterprise::profile::certificate_authority"
            ]["client_whitelist"]
        ):
            group_details["config_data"][
                "puppet_enterprise::profile::certificate_authority"
            ]["client_whitelist"].append(pe_cert_name)

    headers["Content-Type"] = "application/json"
    r = cb_request("POST", url, headers=headers, json=group_details)


def add_to_console_whitelist(api_base_url, pe_usertoken, group_console_id, peconf):
    """
    https://puppet.com/docs/pe/2017.3/api_rbac_activity/rbac_api_v1_forming_requests.html#authentication-using-whitelisted-certificate
    Remote console API access is capable with token or whitelisted-certificate auth
    This is a dependency run-once method using token auth to set the generated certname in the whitelist
    Puppet Ent provides modules with parameters to properly setup the whitelist
    A puppet run is required on the master to complete this configuration
    """
    pe_cert_name = peconf.cert_name
    url = "{}/classifier-api/v1/groups/{}".format(api_base_url, group_console_id)
    headers = {"X-Authentication": pe_usertoken}
    r = cb_request("GET", url, headers=headers)
    group_details = r.json()
    console = group_details["classes"]["puppet_enterprise::profile::console"]
    whitelist = console.get("whitelisted_certnames", [])
    if pe_cert_name not in whitelist:
        whitelist.append(pe_cert_name)
    console["whitelisted_certnames"] = whitelist
    group_details["classes"]["puppet_enterprise::profile::console"] = console
    headers["Content-Type"] = "application/json"
    r = cb_request("POST", url, headers=headers, json=group_details)


def add_to_db_whitelist(api_base_url, pe_usertoken, group_db_id, peconf):
    """
    https://puppet.com/docs/puppetdb/5.1/configure.html#certificate-whitelist
    This is a dependency run-once method using token auth to set the generated certname in the whitelist
    Puppet Ent provides modules with parameters to properly setup the whitelist
    A puppet run is required on the master to complete this configuration
    """
    pe_cert_name = peconf.cert_name
    url = "{}/classifier-api/v1/groups/{}".format(api_base_url, group_db_id)
    headers = {"X-Authentication": pe_usertoken}
    r = cb_request("GET", url, headers=headers)
    group_details = r.json()
    puppetdb = group_details["classes"]["puppet_enterprise::profile::puppetdb"]
    whitelist = puppetdb.get("whitelisted_certnames", [])
    if pe_cert_name not in whitelist:
        whitelist.append(pe_cert_name)
    puppetdb["whitelisted_certnames"] = whitelist
    group_details["classes"]["puppet_enterprise::profile::puppetdb"] = puppetdb
    headers["Content-Type"] = "application/json"
    r = cb_request("POST", url, headers=headers, json=group_details)


def get_node_facts(**kwargs):
    """
    Get node facts for all nodes.

    You must have set up an Master API Connection to the Puppet Master for the
    Configuration Manager.

    If using a split installation where you've entered separate information for
    connecting to the Puppet DB, it should contain the appropriate port for
    connecting to the DB using curl with HTTPS/SSL (8081 by default).
    """
    peconf = kwargs.get("peconf", None)
    if not peconf:
        raise CloudBoltException(
            "Can't run this action without a puppet enterprise configuration!"
        )

    # If there's info for a DB API Connection (split install), use that.
    # Otherwise, we'll default to the master using port 8081.
    api_conn = peconf.master_api_connection
    pe_db_api_conn = peconf.db_api_connection

    api_base_url = "{}://{}:{}".format(
        pe_db_api_conn.protocol if pe_db_api_conn else "https",
        pe_db_api_conn.ip if pe_db_api_conn else api_conn.ip,
        pe_db_api_conn.port if pe_db_api_conn else "8081",
    )

    whitelist_url = "{}://{}:{}".format(api_conn.protocol, api_conn.ip, api_conn.port)
    pe_usertoken = get_puppet_api_rbac_token(
        api_conn.username, api_conn.password, whitelist_url, logger
    )

    # Classification groups in PE that manage the whitelisted-certificates
    groups = get_groups(whitelist_url, pe_usertoken)
    for g in groups:
        if g["name"] == "PE Certificate Authority" or g["classes"].get(
            "puppet_enterprise::profile::certificate_authority"
        ):
            group_ca_id = g["id"]
        if g["name"] == "PE Console" or g["classes"].get(
            "puppet_enterprise::profile::console"
        ):
            group_console_id = g["id"]
        if g["name"] == "PE PuppetDB" or g["classes"].get(
            "puppet_enterprise::profile::puppetdb"
        ):
            group_db_id = g["id"]

    # Ensure connector is added to the Puppet whitelist to allow
    #   remote API calls.
    add_to_ca_whitelist(whitelist_url, pe_usertoken, group_ca_id, peconf)
    add_to_console_whitelist(whitelist_url, pe_usertoken, group_console_id, peconf)
    add_to_db_whitelist(whitelist_url, pe_usertoken, group_db_id, peconf)

    # Only attempt to sign the agent certificate if CB has fetched the signed
    #    whitelisted-certificate
    cert_signed = check_fetch_sign_cert(peconf)

    if cert_signed:
        certnames = kwargs.get("certnames", None)

        if not certnames:
            url = "{}/pdb/query/v4/nodes".format(api_base_url)
            with PuppetRequest(peconf) as r:
                result = r.get(url)
            certnames = [n["certname"] for n in json.loads(result.content)]

        all_facts = []
        for certname in certnames:
            node_facts = {}

            url = "{}/pdb/query/v4/facts".format(api_base_url)
            data = 'query=["=", "certname", "{}"]'.format(certname)

            with PuppetRequest(peconf) as r:
                facts = r.get(url, params=data)
            facts = json.loads(facts.content)

            for f in facts:
                node_facts[f["name"]] = f["value"]

            if not node_facts:
                logger.warning(
                    'Puppet returned no facts for certname "{}".'.format(certname)
                )
                continue

            all_facts.append(node_facts)
    else:
        msg = "CloudBolt Certificate: {} for {} has not been signed".format(
            peconf.cert_name, peconf
        )
        logger.error(msg)
        raise

    return all_facts
