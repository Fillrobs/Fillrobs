"""
Perform cleanup logic after a failed "destructive" Terraform subcommand
(e.g. `terraform destroy`).
"""

from accounts.models import Group
from jobs.models import Job
from utilities.logger import ThreadLogger

logger = ThreadLogger(__name__)


def destroy_failure(job: Job, group: Group, **kwargs) -> None:
    """
    `destroy_failure` runs after a failed `destroy`.

    Note: Any additional side-effects can occur during this function execution,
        but anything returned by this function will not be used.

    Args:
        job (Job): Async "Job" object that's associated with running this `hook`.
        group (Group): "Group" that the original Resource belonged to.
    """
    # Display job progress
    job.set_progress("Handling failed destroy for Terraform Plan")
    return
