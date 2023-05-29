import sys
import time
from common.methods import set_progress

from connectors.puppet_ent.models import PEConf  # noqa: F841, F401
from infrastructure.models import Server
from jobs.models import Job

WAIT_SECONDS = 45


def run(job, logger=None, **kwargs):
    """
    This is the auto_install_agent action that is used by Puppet Enterprise 3.X to boostrap
    a puppet agent onto the node being provisioned and do some initial setup.
    Namely, after bootstrapping the agent it synchronizes nodes with PE and
    makes sure that it was successful.

    The server being provisioned must have credentials configured to
    allow CB to run remote scripts on it.
    """
    script = "curl -k https://{0}:8140/packages/current/install.bash | bash "
    script += "-s main:server={0}"

    # prov jobs only ever have 1 server, so we'll take the first one
    server = job.server_set.first()
    assert isinstance(server, Server)

    conn_conf = kwargs.get("peconf", None)
    if not conn_conf:
        return "", "", ""

    set_progress("Installing Puppet agent on {}.".format(server.hostname))
    server.execute_script(
        script_contents=script.format(conn_conf.hostname), timeout=600
    )

    set_progress(
        "Done installing Puppet agent, waiting {}s for Puppet master to register the "
        "node.".format(WAIT_SECONDS)
    )
    time.sleep(WAIT_SECONDS)

    # sync nodes
    set_progress("Synchronizing nodes with Puppet Enterprise.")
    conn_conf.sync_servers()

    # ensure that the server has a PE node now
    server = Server.objects.get(id=server.id)
    if not hasattr(server, "pe_node"):
        error = "No Puppet Enterprise record found for {} after installing the agent".format(
            server.hostname
        )
        return "FAILURE", "", error

    return "", "", ""


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.stderr.write("usage: %s <Job ID>\n" % sys.argv[0])
        sys.exit(2)

    job_id = sys.argv[1]
    job = Job.objects.get(id=job_id)
    run(job)
