"""
Refreshes ServerStats for servers by executing any action whose name starts with "Refresh
Utilization ".
"""
from cbhooks.models import OrchestrationHook
from common.methods import set_progress


def run(job, logger=None):
    errors = []

    actions = OrchestrationHook.objects.filter(name__startswith="Refresh Utilization ")
    if not actions:
        set_progress("No actions named 'Refresh Utilization *' found.")

    for action in actions:
        action = action.cast()
        set_progress("Running action {}".format(action))
        status, action_output, action_errors = action.run(
            job=job, logger=logger, action=action
        )

        if action_output:
            set_progress("Output:\n{}".format(action_output))
        if action_errors:
            set_progress("Errors:\n{}".format(action_errors))
            errors.append(action_errors)

    return "FAILURE" if errors else "SUCCESS", "", "\n".join(errors)
