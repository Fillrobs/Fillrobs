"""
Post-prov action to automatically decommission the server.

This sample plug-in ships with CloudBolt and is available in Orchestration
Actions > Post-Provisioning so that it executes after every *failed/canceled*
provisioning job.

It can be further constrained to run in only certain resource technologies,
groups, and environments.
"""

from common.methods import create_decom_job_for_servers, set_progress
from jobs.models import Job


def run(job, logger):

    # Get server (there's only ever one per prov job)
    server = job.server_set.first()

    if not server:
        return (
            "SUCCESS",
            "Skipped auto-decom action because server was not created.",
            "",
        )

    if server.status in ["HISTORICAL", "DECOM"]:
        return (
            "SUCCESS",
            "Skipped auto-decom action because server was already decommissioned.",
            "",
        )

    # Optionally add custom logic here to determine whether to delete the
    # server if the action constraints by technology, group, and environment
    # don't suffice.

    set_progress("Job failed. Decommissioning server {}...".format(server))
    decom_jobs = create_decom_job_for_servers([server], owner=job.owner, parent_job=job)

    return Job.wait_for_jobs(decom_jobs)
