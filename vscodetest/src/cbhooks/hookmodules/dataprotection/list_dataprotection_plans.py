from utilities.logger import ThreadLogger

from dataprotection.models import DataProtection


logger = ThreadLogger(__name__)

ALLOW_GROUP_PARAMETER = True


def get_options_list(field, server=None, **kwargs):
    """
    Return a list of data protection plans. Previously, this function filtered based
    on resource type, however this should be done at the environment level using the
    Date Protection Plan Parameter options.
    If the ALLOW_GROUP_PARAMETER is false and options are requested for the parameter
    in a Group context, return an empty option with an explanatory message.
    """
    if not ALLOW_GROUP_PARAMETER:
        return [("", "Not supported for Groups")]

    backends = DataProtection.objects.prefetch_related("protectionplan_set").all()
    options = []
    for backend in backends:
        for plan in backend.protectionplan_set.all():
            plan_spec = plan.specifier
            options.append((plan_spec, plan_spec))
    return options
