"""
Perform cleanup logic after executing "destructive" Terraform subcommands
(e.g. `destroy`).
"""

from accounts.models import Group
from jobs.models import Job
from utilities.logger import ThreadLogger
from cbhooks.models import TerraformStateFile

logger = ThreadLogger(__name__)


def destroy_cleanup(
    job: Job, group: Group, state_file_obj: TerraformStateFile, **kwargs
) -> None:
    """
    `destroy_cleanup` runs after either `post_destroy` or `destroy_failure`,
    as the final step of the "Destroy" workflow, regardless of success or
    failure.

    Note: Any additional side-effects can occur during this function execution,
        but anything returned by this function will not be used.

    Args:
        job (Job): Async "Job" object that's associated with running this `hook`.
        group (Group): "Group" that the original Resource belonged to.
    """
    # Display job progress
    job.set_progress("Running destroy cleanup for Terraform Plan")

    # Remove the state file from the DB
    logger.info(f"Deleting state file '{state_file_obj.module_file.path}'")
    # Delete the module file to not clutter up the filesystem
    state_file_obj.module_file.delete()
    state_file_obj.delete()

    return
