"""
Used to generate options for SSH Keys that can be selected to associate
with a Server, e.g., on the order form
"""
from django.db.models import Q

from orders.models import CustomFieldValue
from utilities.models import SSHKey


def get_options_list(field, environment=None, **kwargs):
    """
    Get and return the CFV options based on the SSH Keys relevant to the
    selected Environment, if any. This only applies if the Environments
    Resource Handler imports RH-specific SSH Keys.

    `field` is passed in, even tho we don't need it.
    `kwargs` is there to ignore any additional parameters that are added to the
    signature of this method later/ that we do not care about.
    """
    options = CustomFieldValue.objects.none()
    if environment and environment.resource_handler:
        # First get all the SSHKey objects connected to the RH and with a reference
        # CFV on the Env
        env_cfv_ids = environment.custom_field_options.values_list("id", flat=True)
        key_filter = Q(resource_handler=environment.resource_handler) & Q(
            key_reference__id__in=env_cfv_ids
        )
        keys = SSHKey.objects.filter(key_filter).values_list("id", flat=True)
        # Then convert to CFVs because that's what actually gets set on objects/ used as options
        options = CustomFieldValue.objects.filter(sshkey__id__in=keys)

    if options.count() == 0:
        # Without the override, the field will be populated with all SSH keys
        # (none of which will have available material)
        return {"initial_value": None, "override": True, "options": []}
    return [(cfv.value, cfv.value) for cfv in options]
