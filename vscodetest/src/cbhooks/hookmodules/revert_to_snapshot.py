"""
CloudBolt Plug-in that revert an OpenStack instance to the most recent snapshot created by CB.
"""
from infrastructure.models import ServerSnapshot
from utilities import events
from utilities.logger import ThreadLogger

logger = ThreadLogger(__name__)


def run(job, *args, **kwargs):
    server = job.server_set.first()
    profile = job.owner
    power_on = server.power_status  # noqa: F841
    rh = server.resource_handler.cast()
    snapshot = ServerSnapshot.objects.filter(server=server).first()
    job.set_progress("Server {} has a snapshot {}".format(server, snapshot))
    job.set_progress(
        "Calling {} to revert {} to snapshot {}".format(rh, server, snapshot)
    )
    try:
        rh.revert_to_snapshot(snapshot, power_on=False)
        server.refresh_info()
        msg = "Server state reverted to snapshot {snapshot}".format(
            snapshot=snapshot.get_name_with_date_created()
        )
        events.add_server_event("MODIFICATION", server, msg, profile, notify_cmdb=True)
    except Exception as err:  # noqa: F841
        return (
            "FAILURE",
            "The snapshot does not exist in OpenStack RH",
            "Make sure your server has snapshot created by CB",
        )
    return ("SUCCESS", "Reverted to snapshot", "")
