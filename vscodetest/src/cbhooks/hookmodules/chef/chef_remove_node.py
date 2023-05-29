"""
Delete the node with the specified name from the chef server.
Also delete the client with the same name.

Return None on success, raise an exception otherwise.  If the node
and/or client are already not present in the Chef server, proceed and
treat the deletion as a success.
"""
import chef
from utilities.run_command import run_command
from utilities.exceptions import CommandExecutionException
from utilities.logger import ThreadLogger


logger = ThreadLogger(__name__)


def run(*args, **kwargs):
    node_name = kwargs.get("node_name", "")
    knife_config_path = kwargs.get("knife_config_path", "")

    try:
        node = chef.Node(node_name)
        node.delete()
    except chef.exceptions.ChefServerNotFoundError:
        # the node has already been deleted, that is okay
        pass

    cmd = "knife client delete {} -c {} -y".format(node_name, knife_config_path)
    try:
        run_command(cmd)
    except CommandExecutionException as e:
        # check if failure was due to it not being found
        if e.rv == 100 and e.output.startswith(
            "ERROR: The object you are looking for could not be found"
        ):
            # it was, therefore pass
            pass
        else:
            # it was some other CommandExecutionException, raise it
            raise
