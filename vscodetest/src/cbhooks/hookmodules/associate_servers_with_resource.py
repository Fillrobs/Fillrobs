#!/usr/local/bin/python

from common.methods import set_progress
from infrastructure.models import Server
from servicecatalog.models import ServiceItem
from utilities.events import add_resource_event, add_server_event

"""
Run as a Resource Action to associate existing CB servers with the given
deployed resource. The servers must be associated with an existing tier.

No actual changes are made to the VMs or anything else that's part of the
resource, such as load balancers. No actions are run. The server's resource &
service_item attributes are simply updated so it appears as part of the resource
in that tier.
"""


def run(job, **kwargs):
    params = job.job_parameters.cast()
    resource = params.resources.first()
    tier_id = "{{ service_item }}"
    servers_to_associate = {{servers_to_associate}}  # noqa: E201, E202, F821
    servers_to_associate = [
        Server.objects.get(id=svr_id) for svr_id in servers_to_associate
    ]
    if not tier_id or "{{ tier" in tier_id:
        raise TypeError("Tier ID parameter is required but was not specified.")
    if not servers_to_associate:
        raise TypeError(
            "Servers to Associate parameter is required but was not specified."
        )

    tier = ServiceItem.objects.get(id=tier_id).cast()

    set_progress(
        "Associating server(s) {} with resource {}".format(
            ", ".join([s.hostname for s in servers_to_associate]), resource.name
        ),
        job,
    )

    final_results = ("SUCCESS", "", "")
    for server in servers_to_associate:
        server.resource = resource
        server.service_item = tier
        add_server_event(
            "INFO",
            server,
            "Server associated with resource {}".format(resource),
            job=job,
            profile=job.owner,
        )
        server.save()

    add_resource_event(
        "MODIFICATION",
        resource,
        "Associated server(s) with resource: {}.".format(
            ", ".join([s.hostname for s in servers_to_associate])
        ),
        job=job,
        profile=job.owner,
    )

    return final_results


def generate_options_for_servers_to_associate(profile=None, **kwargs):
    """
    Returns a list of server choices, namely the set of Servers that the user
    has change_attributes permissions for and are not already associated with
    a Resource.
    """
    if not profile:
        return []
    servers = Server.objects.exclude(status="HISTORICAL").filter(resource=None)
    if not (profile.is_super_admin or profile.devops_admin):
        groups = profile.get_groups_for_permission("server.change_attributes")
        servers = servers.filter(group__in=groups)
    options = [(svr.id, svr.hostname) for svr in servers]
    return options


def generate_options_for_service_item(resource=None, **kwargs):
    """
    Returns a list of PSSI choices, which are used as options for acting on a
    specific tier of the deployed resource.
    """
    if not resource:
        return []
    blueprint = resource.blueprint
    options = [(pssi.id, pssi.name) for pssi in blueprint.pssis()]
    return options
