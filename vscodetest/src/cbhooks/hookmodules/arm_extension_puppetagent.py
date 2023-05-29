"""
Provisions the PuppetAgent extension on one or more servers.
"""
from common.methods import set_progress
from servicecatalog.models import ProvisionServerServiceItem

# Change the following section when developing an action for a new extension.

EXTENSION_NAME = "PuppetAgent"
PUBLISHER = "Puppet"
VERSION = "1.5"

settings = {}
protected_settings = {"PUPPET_MASTER_SERVER": "{{ puppet_master_fqdn }}"}


# Below here is generic code for installing an ARM extension.


def generate_options_for_server_tier(resource=None, blueprint=None, **kwargs):
    if resource:
        blueprint = resource.blueprint

    if blueprint:
        return [(pssi.name, pssi.name) for pssi in blueprint.pssis()]
    else:
        return []


def run(job=None, logger=None, resource=None, server=None, **kwargs):
    """
    Install an extension on the specified server or server tier.

    Can be used as a server action, a resource action, or a blueprint action.
    """
    server_tier = "{{ server_tier }}"
    if server:
        servers = [server]
        target = server.hostname
    elif server_tier:
        pssi = ProvisionServerServiceItem.objects.get(
            name=server_tier, blueprint=resource.blueprint
        )
        servers = resource.server_set.filter(service_item=pssi)
        target = "{} servers on {}".format(servers.count(), server_tier)
    else:
        servers = resource.server_set.all()
        target = "{} servers on all tiers".format(servers.count())

    set_progress("Adding {} extension to {}".format(EXTENSION_NAME, target))
    resource_handler = servers[0].resource_handler.cast()
    result_dict = resource_handler.add_extension(
        servers, EXTENSION_NAME, PUBLISHER, VERSION, settings, protected_settings
    )

    has_failures = False
    for hostname, result in list(result_dict.items()):
        if isinstance(result, Exception):
            set_progress(
                "Failed to install extension on {} due to {}".format(
                    hostname, result.__class__.__name__
                )
            )
            has_failures = True

    status = "FAILURE" if has_failures else "SUCCESS"
    return status, "", ""
