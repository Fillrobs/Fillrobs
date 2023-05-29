"""
Perform teardown and integration logic after executing "constructive" Terraform
subcommands (e.g. `init`, `plan`, and `apply`).
"""

from typing import List

from accounts.models import Group
from cbhooks.models import TerraformStateFile, TerraformPlanHook
from infrastructure.models import Environment, Server
from jobs.models import Job
from resources.models import Resource
from utilities.logger import ThreadLogger

logger = ThreadLogger(__name__)

# These are the names of Terraform resources associated with servers/VMs in the
# main Terraform Providers which have corresponding CloudBolt Resource
# Technology support. Used below in `_parse_state_file_for_server_ids()` for
# finding servers in a state file.
TERRAFORM_VM_TYPES = [
    "google_compute_instance",
    "azurerm_virtual_machine",
    "aws_instance",
    "vsphere_virtual_machine",
    "openstack_compute_instance_v2",
    "clc_server",
    "nutanix_virtual_machine",
]


def post_provision(
    hook: TerraformPlanHook,
    job: Job,
    resource: Resource,
    state_file_obj: TerraformStateFile,
    group: Group,
    **kwargs,
) -> str:
    """
    `post_provision` runs after `apply`, after a Terraform Plan action has
    provisioned one or more Resources.

    This function adds any servers provisioned by Terraform as "Server" objects
    in CloudBolt, allowing for management in this product.

    Note: This function _must_ return a `str. Any additional side-effects can
        occur during this function execution, but changing the return type will
        cause Terraform execution to break.

    Args:
        hook (TerraformPlanHook): The "Terraform Plan" Action that's called from
            a Blueprint.
        job (Job): Async "Job" object that's associated with running this `hook`.
        resource (Resource): "Resource" object that Terraform will populate /
            provision to.
        state_file_obj (TerraformStateFile): File model object for the generated
            Terraform state file.
        group (Group): "Group" that the original Blueprint was ordered under.

    Returns:
        str: Output to be displayed on the Job "Details" page.
    """
    servers: List[Server] = get_or_create_server_records_from_state_file(
        state_file_obj=state_file_obj, resource=resource, group=group
    )

    return (
        f"Created resource '{resource}' with " f"{len(servers)} servers from terraform"
    )


def get_or_create_server_records_from_state_file(
    state_file_obj: TerraformStateFile, resource: Resource, group: Group,
) -> List[Server]:
    """
    Get or create Server object instances from server's unique UUIDs parsed out of
    the Terraform state file from this action.
    """

    server_ids = _parse_state_file_for_server_ids(state_file_obj)
    logger.info(
        f"Will create or update records for {len(server_ids)} servers in CloudBolt."
    )
    unassigned_env = Environment.objects.get(name="Unassigned")
    servers = []

    for svr_id in server_ids:
        if svr_id:
            # Server manager does not have the create_or_update method,
            # so we do this manually.
            try:
                server = Server.objects.get(resource_handler_svr_id=svr_id)
                server.resource = resource
                server.group = group
                server.owner = resource.owner
                server.environment = unassigned_env
                server.save()
                logger.info(f"Found existing server record: '{server}'")
            except Server.DoesNotExist:
                logger.info(
                    f"Creating new server with resource_handler_svr_id "
                    f"'{svr_id}', resource '{resource}', group '{group}', "
                    f"owner '{resource.owner}', and "
                    f"environment '{unassigned_env}'"
                )
                server = Server(
                    hostname=svr_id,
                    resource_handler_svr_id=svr_id,
                    resource=resource,
                    group=group,
                    owner=resource.owner,
                    environment=unassigned_env,
                )
                server.save()
                # We have to have already saved the new server record before this
                # will effectively be added as a custom field value, then
                # we have to save again to apply that relationship.
                server.created_by_terraform = True
                server.save()

            servers.append(server)

    return servers


def _parse_state_file_for_server_ids(state_file_obj: TerraformStateFile) -> List[int]:
    """
    Read through the JSON dict of the state file getting resource ids if they
    are expected to be servers.

    Args:
        state_file_obj (cbhooks.TerraformStateFile)
    """
    server_ids = []

    logger.info(
        f"Parsing the JSON from the state file "
        f"'{state_file_obj.module_file.name}' to "
        f"search for servers that can be represented in CloudBolt."
    )

    state_dict = state_file_obj.content_json
    if not state_dict:
        return []

    # Terraform pushes out versions of their state file syntax, and we are only
    # able to support version 3 (will support 4 later, too)
    version = int(state_dict.get("version"))

    # Parse modules.
    # The JSON is slightly different depending on whether the plan contains modules
    modules = state_dict.get("modules")
    if modules:
        resources = []
        for module in modules:
            resources_dict = module.get("resources")
            for resource_name, attrs in resources_dict.items():
                resources.append(attrs)
    else:
        # Parse the resources directly.
        resources = state_dict.get("resources", [])

    for resource_dict in resources:
        # Expected format (version 3):
        # resource_dict = {
        #     'type': 'aws_instance',
        #     'primary': {
        #          'id': 'i-08204873902849032'
        #      }
        # }
        if resource_dict.get("type") in TERRAFORM_VM_TYPES:
            logger.info(
                f"Found a terraform resource of type '{resource_dict.get('type')}'."
            )
            if version == 3:
                vm_id = resource_dict.get("primary", {}).get("id")
                if vm_id:
                    server_ids.append(vm_id)
            else:
                logger.warning(
                    f"Detected that the state file's version is "
                    f"{version} and CloudBolt currently only supports"
                    f"version 3."
                )
                if version == 4:
                    # We shouldn't be able to get to this step because Terraform
                    # variable - action input parsing should fail first,
                    # but we have left this code here for future support.
                    instances = resource_dict.get("instances")
                    for instance in instances:
                        vm_id = instance.get("attributes").get("id")
                        server_ids.append(vm_id)

    return server_ids
