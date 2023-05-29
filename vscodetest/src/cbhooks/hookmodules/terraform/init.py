"""
Defines the behavior that CloudBolt uses when calling the underlying `terraform
init` command.
"""

from typing import Dict, List, Tuple

from cbhooks.models import TerraformPlanHook
from jobs.models import Job
from resources.models import Resource
from servicecatalog.models import RunTerraformPlanHookServiceItem
from utilities.logger import ThreadLogger

logger = ThreadLogger(__name__)

# Type definitions

# Returns flags (List[str]) and environment variables (Dict[str, str]) specific
# to this this command (e.g. `terraform init`).
output = Tuple[List[str], Dict[str, str]]


def init(
    hook: TerraformPlanHook,
    job: Job,
    action_inputs: dict,
    resource: Resource,
    service_item: RunTerraformPlanHookServiceItem,
    tf_env_vars: Dict[str, str],
    **kwargs,
) -> output:
    """
    `init` runs after `pre_provision`, and returns flags and environment
    variables used by the underlying `terraform init` command.

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
        tf_env_vars (Dict[str, str]): Environment variables used by Terraform
            for this command (`terraform init`).
    """
    job.set_progress("Running Terraform init.")

    # Set flags to be called by `terraform init`
    flags: List[str] = ["-no-color", "-input=false"]

    # Optionally update the TF environment variables for `terraform init`
    # tf_env_vars["..."] = ...

    return flags, tf_env_vars
