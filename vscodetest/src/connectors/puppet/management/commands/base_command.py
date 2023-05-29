from __future__ import unicode_literals
from __future__ import print_function
import subprocess

from django.core.management.base import BaseCommand


class BasePuppetConfCommand(BaseCommand):

    """
    This common mgmt cmd provides a common way to run subprocesses and
    update the conf state, and helps reduce boilerplate code.
    """

    def run_cmd_and_update_state(
        self, cmd, puppet_conf, success_state, error_state, error_msg
    ):
        """
        Attempt to run a subprocess and update the conf's state as
        appropriate.  This is a common pattern used by a couple of
        management commands.
        """
        print(" ".join(cmd))
        try:
            print(subprocess.check_output(cmd))
            puppet_conf.cert_state = success_state
            puppet_conf.cert_message = ""
        except subprocess.CalledProcessError as e:
            puppet_conf.cert_state = error_state
            puppet_conf.cert_message = (
                error_msg + "\n  Command: {}\n" "  Output: {}"
            ).format(e.cmd, e.output)
        puppet_conf.save()
