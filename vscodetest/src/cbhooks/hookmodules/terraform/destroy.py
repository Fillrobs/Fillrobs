"""
Defines the behavior that CloudBolt uses when calling the underlying `terraform
destroy` command.

Note: This plugin runs _once per Terraform state file_.
"""

from typing import Dict, List, Tuple

from cbhooks.models import TerraformPlanHook, TerraformStateFile
from jobs.models import Job
from resources.models import Resource
from utilities.logger import ThreadLogger

logger = ThreadLogger(__name__)

# Type definitions

# Returns flags (List[str]) and environment variables (Dict[str, str]) specific
# to this this command (e.g. `terraform destroy`).
output = Tuple[List[str], Dict[str, str]]


def destroy(
    hook: TerraformPlanHook,
    job: Job,
    resource: Resource,
    tf_env_vars: Dict[str, str],
    state_file_obj: TerraformStateFile,
    state_file_path: str,
    **kwargs,
) -> output:
    """
    `destroy` runs after `pre_destroy`, and returns flags and environment
    variables used by the underlying `terraform destroy` command.

    Note: This function _must_ return the `output` Tuple. Any additional
        side-effects can occur during this function execution, but changing
        the return type will cause Terraform execution to break.

    Args:
        hook (TerraformPlanHook): The "Terraform Plan" Action that's called from
            a Blueprint.
        job (Job): Async "Job" object that's associated with running this `hook`.
        resource (Resource): "Resource" object that will be removed by this action.
        tf_env_vars (Dict[str, str]): Environment variables used by Terraform
            for this command (`terraform destroy`).
    """
    # Display job progress
    job.set_progress("Running Terraform destroy")

    # Set flags to be called by `terraform destroy`
    flags: List[str] = [
        "-no-color",
        "-input=false",
        "-auto-approve",
        f"-state={state_file_path}",
    ]

    # Optionally update the TF environment variables for `terraform dstroy`
    # tf_env_vars["..."] = ...

    return flags, tf_env_vars
