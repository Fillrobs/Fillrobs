"""
Defines the behavior that CloudBolt uses when calling the underlying `terraform
apply` command.
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
# to this this command (e.g. `terraform apply`).
output = Tuple[List[str], Dict[str, str]]


def apply(
    hook: TerraformPlanHook,
    job: Job,
    action_inputs: dict,
    resource: Resource,
    service_item: RunTerraformPlanHookServiceItem,
    tf_env_vars: dict,
    state_file_path: str,
    plan_file: str,
    plan_output: str,
    var_file: str = None,
    **kwargs,
) -> output:
    """
    `apply` runs after `plan`, and returns flags and environment variables used
    by the underlying `terraform apply` command.

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
            for this command (`terraform apply`).
        state_file_path (str): Absolute file path to the generated Terraform
            state file.
        plan_file (str): Absolute file path to the Terraform plan file.
        plan_output (str): Stdout output from running `terraform plan` in the
            previous step.
        var_file (str): (Optional) Absolute file path to the Terraform
            variables file.
    """
    # Optionally pause the job and wait for User confirmation.
    pause_job = action_inputs.get("confirm_terraform_plan", False)
    if pause_job:
        job.output = "\n".join(plan_output)
        # Wait for the user to confirm they want this to apply
        job.set_progress(
            "Please review the above Terraform Plan and continue if it looks good."
        )
        job.pause()
        job.output = ""

    job.set_progress("Running Terraform apply.")

    # Set flags to be passed to `terraform apply`
    flags: List[str] = [
        "-no-color",
        "-input=false",
        "-auto-approve",
        f"-state-out={state_file_path}",
    ]

    # Specify the Terraform state file
    if state_file_path is not None and plan_file is None:
        flags.append(f"-state={state_file_path}")

    # Pass Terraform variables file
    if var_file is not None:
        flags.append(f"-var-file={var_file}")

    # Specify a backup file
    if state_file_path is not None:
        flags.append(f"-backup={state_file_path}.backup")

    # Optionally update the TF environment variables for `terraform apply`
    # tf_env_vars["..."] = ...

    return flags, tf_env_vars
