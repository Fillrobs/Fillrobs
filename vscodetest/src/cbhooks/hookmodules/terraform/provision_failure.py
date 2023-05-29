"""
Performs teardown and cleanup after any failed "constructive" Terraform
subcommands (e.g. `init`, `plan`, and `apply`).
"""

from accounts.models import Group
from jobs.models import Job
from resources.models import Resource
from utilities.logger import ThreadLogger

logger = ThreadLogger(__name__)


def provision_failure(job: Job, group: Group, resource: Resource, **kwargs) -> None:
    """
    `provision_failure` runs after a failed 'constructive' action, namely
    `init`, `plan`, or `apply`.

    Note: Any additional side-effects can occur during this function execution,
        but anything returned by this function will not be used.

    Args:
        job (Job): Async "Job" object that's associated with running this `hook`.
        group (Group): "Group" that the original Resource belonged to.
        resource (Resource): "Resource" object that Terraform will populate /
            provision to.
    """
    # Display job progress
    job.set_progress("Handling failed provision for Terraform Plan")

    # Remove any CloudBolt "Resources" if provision failed.
    resource.delete()
    return
