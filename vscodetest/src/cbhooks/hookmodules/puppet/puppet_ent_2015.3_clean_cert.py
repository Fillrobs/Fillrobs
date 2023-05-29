"""
https://puppet.com/docs/puppet/5.4/http_api/http_certificate_status.html
https://puppet.com/docs/puppet/5.4/schemas/host.json
https://puppet.com/docs/puppetdb/6.0/api/admin/v1/cmd.html
"""
from connectors.puppet_ent.puppet_ent_api import PuppetRequest
from connectors.puppet_ent.models import PEConf  # noqa: F401
from utilities.logger import ThreadLogger
from common.methods import set_progress
from utilities.exceptions import CloudBoltException
import requests
import json
import datetime

LOGGER = ThreadLogger(__name__)


def revoke_cert(peconf, certname):
    base_url = "https://{}:8140".format(peconf.hostname)
    url = "{}/puppet-ca/v1/certificate_status/{}".format(base_url, certname)
    data = '{"desired_state":"revoked"}'

    with PuppetRequest(peconf) as r:
        try:
            result = r.put(url, data=data)
        except requests.HTTPError as err:
            # Ignore 404s - it's okay if the cert is already gone
            result = {}
            if err.response.status_code != 404:
                raise

    return result


def delete_cert(peconf, certname):
    base_url = "https://{}:8140".format(peconf.hostname)
    url = "{}/puppet-ca/v1/certificate_status/{}".format(base_url, certname)

    with PuppetRequest(peconf) as r:
        try:
            result = r.delete(url)
        except requests.HTTPError as err:
            # Ignore 404s - it's okay if the cert is already gone
            result = {}
            if err.response.status_code != 404:
                raise

    return result


def purge_node(peconf, certname):
    base_url = "https://{}:8081".format(peconf.hostname)
    url = "{}/pdb/cmd/v1".format(base_url)
    time_in_iso = datetime.datetime.utcnow().isoformat()

    data = {}
    data["command"] = "deactivate node"
    data["version"] = 3
    data["payload"] = {}
    payload = {}
    payload["certname"] = certname
    payload["producer_timestamp"] = str(time_in_iso)
    data["payload"] = payload
    json_data = json.dumps(data)

    with PuppetRequest(peconf) as r:
        result = r.post(url, data=json_data)

    return result


def clean_cert(job=None, logger=None, **kwargs):
    """
    This is the clean_cert action that is used by Puppet Enterprise 2015.3 to
    revoke end delete the certificate of an deleted Puppet node and purge the
    node from the Puppet Enterprise master.
    """

    #    server = kwargs.get('server', None)
    #    cert_name = server.hostname + '.' + server.domain
    cert_name = kwargs.get("certname", None)

    # peconf = server.environment.get_connector_confs().first().cast()
    peconf = kwargs.get("peconf", None)
    if not peconf:
        raise CloudBoltException(
            "Can't run this action without a puppet enterprise configuration!"
        )

    revoke_cert(peconf, cert_name)
    set_progress("Certificate {} revoked.".format(cert_name))

    delete_cert(peconf, cert_name)
    set_progress("Certificate {} deleted.".format(cert_name))

    purge_node(peconf, cert_name)
    set_progress("Node {} purged.".format(cert_name))

    return "SUCCESS", "", ""
