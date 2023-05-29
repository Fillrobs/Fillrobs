"""
https://puppet.com/docs/puppet/5.4/http_api/http_certificate_status.html
https://puppet.com/docs/puppet/5.4/schemas/host.json
"""
from connectors.puppet_ent.puppet_ent_api import PuppetRequest
from connectors.puppet_ent.models import PEConf
from utilities.helpers import cb_request
from utilities.logger import ThreadLogger
from common.methods import set_progress
import requests
import time

logger = ThreadLogger(__name__)


def node_facts(peconf, certname):
    base_url = "https://{}:8140".format(peconf.hostname)
    url = "{}/puppet/v3/node/{}".format(base_url, certname)
    with PuppetRequest(peconf) as r:
        result = r.get(url).json()
    return result


def kick_master(peconf, pe_usertoken, master_env):
    """
    https://puppet.com/docs/pe/2016.4/orchestrator_api_commands.html
    The orchestrator API is used for kicking off a puppet run
    """
    base_url = "https://{}".format(peconf.hostname)
    url = "{}/orchestrator/v1/command/deploy".format(base_url)

    payload_run = {"environment": master_env, "scope": {"nodes": [peconf.hostname]}}
    headers = {"X-Authentication": pe_usertoken}

    with PuppetRequest(peconf) as r:
        result = r.post(url, data=None, json=payload_run, headers=headers)

    return result


def sign_cert(peconf, certname):
    """
    Sign the certificate
    The whitelisted certificated is required for this endpoint
    """
    base_url = "https://{}:8140".format(peconf.hostname)
    url = "{}/puppet-ca/v1/certificate_status/{}".format(base_url, certname)
    payload_signed = {"desired_state": "signed"}

    set_progress("Signing Certificate: {}".format(certname))
    with PuppetRequest(peconf) as r:
        result = r.put(url, data=None, json=payload_signed)

    return result


def get_cert(peconf, certname):
    """
    Look up the certificate details
    The whitelisted certificated is required for this endpoint
    """
    base_url = "https://{}:8140".format(peconf.hostname)
    url = "{}/puppet-ca/v1/certificate_status/{}".format(base_url, certname)

    with PuppetRequest(peconf) as r:
        try:
            result = r.get(url).json()
        except requests.HTTPError as err:
            result = {}
            if err.response.status_code == 403:
                set_progress("Failed to fetch whitelisted certificate.")

                msg = """Cloudbolt permissions have not been updated on the
                PE Master. Please trigger a puppet run on the puppet master
                or wait for the next scheduled PE Master run to finish."""
                logger.debug(msg)
                raise
            # Ignore 404s - it's okay if the cert is already gone
            elif err.response.status_code != 404:
                raise
    return result


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


def get_groups(api_base_url, pe_usertoken):
    """
    Get a list of classification groups in the PE console
    """
    url = "{}/classifier-api/v1/groups".format(api_base_url)
    headers = {"X-Authentication": pe_usertoken}
    r = cb_request("GET", url, headers=headers)
    return r.json()


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


def run(job=None, logger=None, **kwargs):
    cert_name = kwargs.get("cert_name", None)

    peconf_id = kwargs.get("peconf_id", None)
    peconf = PEConf.objects.get(id=peconf_id)

    pe_usertoken = kwargs.get("pe_usertoken", None)

    api_conn = peconf.master_api_connection
    api_base_url = "{}://{}:{}".format(api_conn.protocol, api_conn.ip, api_conn.port)

    # Classification groups in PE that manage the whitelisted-certificates
    groups = get_groups(api_base_url, pe_usertoken)
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

    # A puppet run is required on the master to complete this configuration

    add_to_ca_whitelist(api_base_url, pe_usertoken, group_ca_id, peconf)
    add_to_console_whitelist(api_base_url, pe_usertoken, group_console_id, peconf)
    add_to_db_whitelist(api_base_url, pe_usertoken, group_db_id, peconf)

    # Only attempt to sign the agent certificate if CB has fetched the signed
    #    whitelisted-certificate
    cert_signed = check_fetch_sign_cert(peconf)
    if cert_signed:
        set_progress("Waiting to sign certificate: {}".format(cert_name))
        state = None
        count = 1
        # Default puppet agent waitforcert display is 120 seconds
        # Exceeding 2 default attempts by a 5 second count
        while count != 50 and state != "signed":
            csr = get_cert(peconf, cert_name)
            state = csr.get("state", "Not Found")
            set_progress('Attempt: {} Certificate State: "{}"'.format(count, state))
            if state == "requested":
                set_progress("Found Certificate: {}".format(cert_name))
                sign_cert(peconf, cert_name)
            else:
                count += 1
                time.sleep(5)
    else:
        msg = "CloudBolt Certificate: {} for {} has not been signed".format(
            peconf.cert_name, peconf
        )
        return "FAILURE", "", msg

    return "SUCCESS", "", ""
