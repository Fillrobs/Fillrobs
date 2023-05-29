"""
Perform cleanup logic after executing "constructive" Terraform subcommands
(e.g. `init`, `plan`, and `apply`).
"""

import os

from accounts.models import Group
from cbhooks.models import TerraformPlanHook, TerraformStateFile
from jobs.models import Job
from resources.models import Resource
from utilities.logger import ThreadLogger


logger = ThreadLogger(__name__)


def provision_cleanup(
    hook: TerraformPlanHook,
    job: Job,
    resource: Resource,
    plan_file: str,
    state_file_obj: TerraformStateFile,
    group: Group,
    **kwargs,
) -> None:
    """
    `provision_cleanup` runs after either `post_provision` or
    `provision_failure`, as the final step of the "Provision" workflow,
    regardless of success or failure.

    Note: Any additional side-effects can occur during this function execution,
        but anything returned by this function will not be used.

    Args:
        hook (TerraformPlanHook): The "Terraform Plan" Action that's called from
            a Blueprint.
        job (Job): Async "Job" object that's associated with running this `hook`.
        resource (Resource): "Resource" object that Terraform will populate /
            provision to.
        plan_file (str): Absolute file path to the Terraform plan file.
        state_file_obj (TerraformStateFile): File model object for the generated
            Terraform state file.
        group (Group): "Group" that the original Blueprint was ordered under.
    """
    # Cleanup the generated Terraform Plan file on disk
    if os.path.isfile(plan_file):
        os.remove(plan_file)

    return
