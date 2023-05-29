"""
Perform setup logic before executing "constructive" Terraform subcommands
(e.g. `init` `plan`, and `apply`).
"""

import os
import pwd
from typing import Dict, Tuple, Union

from django.conf import settings
from django.core.files.base import ContentFile

from cbhooks.models import TerraformPlanHook, TerraformStateFile
from cbhooks.services import TerraformFileService
from common.methods import get_proxies, get_bypass_proxy_domains
from jobs.models import Job
from resources.models import Resource
from servicecatalog.models import (
    RunTerraformPlanHookServiceItem,
    TerraformConfigServiceItem,
)
from utilities.logger import ThreadLogger

logger = ThreadLogger(__name__)

# Type definitions
tf_env_vars_type = Dict[str, str]
plan_file_type = str

# Returns Terraform environment variables (Dict[str, str]), the Terraform
# state file object (TerraformStateFile), and the Terraform plan file path (str)
# for use in downstream commands (e.g. `terraform init`, `terraform plan`, etc.)
output = Tuple[tf_env_vars_type, TerraformStateFile, plan_file_type]
TerraformServiceItemType = Union[
    RunTerraformPlanHookServiceItem, TerraformConfigServiceItem
]


def pre_provision(
    hook: TerraformPlanHook,
    job: Job,
    action_inputs: dict,
    resource: Resource,
    service_item: TerraformServiceItemType,
    **kwargs: dict,
) -> output:
    """
    `pre_provision` runs before any "constructive" Terraform subcommands, e.g.
    `init`, `plan`, and `apply`, and sets up the global, required state.

    Note: This function _must_ return the `output` Tuple. Any additional
        side-effects can occur during this function execution, but changing
        the return type will cause Terraform execution to break.

    Args:
        hook (TerraformPlanHook): The "Terraform Plan" Action that's called from
            a Blueprint.
        job (Job): Async "Job" object that's associated with running this `hook`.
        action_inputs (dict): Map of key:value variables that are passed to this
            Terraform Action.
        resource (Resource): "Resource" object that Terraform will populate /
            provision to.
        service_item (RunTerraformPlanHookServiceItem): The Blueprint item
            associated with this "Terraform Plan" Action.
    """
    # Set progress on the Job page.
    job.set_progress(f"Running pre-provision for Terraform Plan {service_item.name}")

    # Get or create a state file. Creation will start an empty one.
    state_file_obj, created = get_or_create_state_file(hook, resource, service_item)

    # Re-extract the plan from git if the hook is wants us to.
    if getattr(hook, "refresh_on_order", False):
        logger.info("Attempting to update the configuration source...")
        TerraformFileService(hook=hook).extract_plan_file(
            local_path_override=hook.local_path
        )

    # Set the action inputs and Terraform variables.
    _ = resource.set_terraform_vars(state_file_obj.id, action_inputs)
    tf_env_vars: tf_env_vars_type = resource.get_terraform_vars(state_file_obj.id)

    # The `.tfplan` file we will store our plan in.
    # This is stored temporarily while we plan and then apply.
    # It is cleaned up immediately after the `apply` finishes.
    tf_plans_dir = settings.TERRAFORM_TFPLANS_DIR
    if not os.path.isdir(tf_plans_dir):
        os.mkdir(tf_plans_dir)
    plan_file: plan_file_type = os.path.join(tf_plans_dir, f"{job.id}.tfplan")

    # Add proxy information to TF environment variables.
    proxies = get_proxies("hashicorp.com")
    no_proxies_list = get_bypass_proxy_domains()
    no_proxies = ",".join(no_proxies_list)

    tf_env_vars.setdefault("HTTP_PROXY", proxies.get("http", ""))
    tf_env_vars.setdefault("HTTPS_PROXY", proxies.get("https", ""))
    tf_env_vars.setdefault("NO_PROXY", no_proxies)

    return tf_env_vars, state_file_obj, plan_file


def get_or_create_state_file(
    hook: TerraformPlanHook, resource: Resource, service_item: TerraformServiceItemType,
) -> Tuple[TerraformStateFile, bool]:
    """
    Gets unique state files by querying by resource and service item and updates
    the source_code_url (which is the plan path) in the defaults for creation.
    """
    # We accept two kinds of SI, but they each have their own FK relationship on
    # the model, so we need to know which type to persist
    si_type = (
        "service_item"
        if type(service_item) == RunTerraformPlanHookServiceItem
        else "config_service_item"
    )
    file_args = {"resource": resource, "hook": hook, si_type: service_item}
    state_file, created = TerraformStateFile.objects.get_or_create(**file_args)

    if created:
        # Then create a new, empty module_file
        new_filename = state_file.build_filename()
        state_file.module_file.save(new_filename, ContentFile(""))  # empty content
        logger.info(f"Created a new empty state file {state_file.module_file.name}.")
    else:
        logger.info(f"Got an existing state file {state_file.module_file.name}.")

    logger.info(f"Changing ownership of {state_file.module_file.path} to apache:apache")
    try:
        # If we are on a system with the apache user, set that to the statefile owner
        gid = pwd.getpwnam("apache").pw_gid
        uid = pwd.getpwnam("apache").pw_uid
        os.chown(state_file.module_file.path, uid, gid)
    except KeyError:
        # We do not have the apache user, so we will keep the owner as root.
        pass

    return state_file, created
