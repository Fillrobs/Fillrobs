#!/usr/bin/env python
from __future__ import print_function
import sys

if __name__ == "__main__":
    import django

    django.setup()

from common.methods import set_progress
from infrastructure.models import Server
from infrastructure.models import ServerSnapshot


def run(job, logger, snapshot_list=None, **kwargs):
    if not snapshot_list:
        params = job.job_parameters.cast().arguments
        snapshot_list = params["snapshots"]

    num_snapshots = len(snapshot_list)
    set_progress(
        "Deleting {} snapshot(s)".format(num_snapshots),
        tasks_done=0,
        total_tasks=num_snapshots,
    )
    current_snapshot = 1
    errors = []
    for server_id, snapshot_id in snapshot_list:
        server = Server.objects.get(id=server_id)
        msg = "Deleting snapshot {}/{}: #{} on {}".format(
            current_snapshot, num_snapshots, snapshot_id, server
        )
        set_progress(msg, tasks_done=current_snapshot - 1)

        rh = server.resource_handler.cast()

        # delete the snapshot record from the CB DB first, if one exists
        snapshot_obj = ServerSnapshot.objects.filter(
            server_id=server_id, identifier=snapshot_id
        ).first()
        if snapshot_obj:
            snapshot_obj.delete()

        # Create a temporary ServerSnapshot object in memory (not saved to the DB), just to pass
        # to the RH's delete_snapshot() method.
        tmp_snapshot_obj = ServerSnapshot(server=server, identifier=snapshot_id)

        try:
            rh.delete_snapshot(tmp_snapshot_obj)
        except Exception as err:
            msg = "Problem deleting snapshot {} on {}".format(snapshot_id, server)
            logger.exception(msg)
            errors.append("{}: {}".format(msg, err))
        current_snapshot += 1

    if errors:
        err_string = " \n".join(errors)
        return "FAILURE", "", err_string

    return "", "", ""


# The next lines enable this module to be run as a script from the command line for a fast test-dev
# cycle
if __name__ == "__main__":
    server_id = sys.argv[1]
    snapshot_id = sys.argv[2]
    print(run(job=None, logger=None, snapshot_list=[(server_id, snapshot_id)]))
