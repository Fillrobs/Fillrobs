"""
Perform teardown and verification logic after executing "destructive" Terraform
subcommands (e.g. `destroy`).
"""

from accounts.models import Group
from jobs.models import Job
from utilities.logger import ThreadLogger

logger = ThreadLogger(__name__)


def post_destroy(job: Job, group: Group, **kwargs) -> None:
    """
    `post_destroy` runs after `destroy`, after deleting one or more Resources
    provisioned by a Terraform Plan action.

    Note: Any additional side-effects can occur during this function execution,
        but anything returned by this function will not be used.

    Args:
        job (Job): Async "Job" object that's associated with running this `hook`.
        group (Group): "Group" that the original Resource belonged to.
    """
    # Display job progress
    job.set_progress("Running post-destroy for Terraform Plan")

    return
