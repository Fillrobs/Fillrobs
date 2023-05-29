from common.methods import get_predefined_cfv_from_si
from resourcehandlers.alibaba.alibaba_wrapper import (
    TechnologyWrapper as AlibabaTechnologyWrapper,
)
from resourcehandlers.alibaba.models import AlibabaResourceHandler


def get_options_list(
    field, control_value=None, service_item=None, **kwargs,
):
    """
    Regenerate options for Alibaba instance types on the order form based on what zone is selected.
    """
    environment = kwargs.get("environment")
    zone_id = control_value

    if environment and zone_id:
        initial_value = get_predefined_cfv_from_si(
            service_item, environment, field.name
        )
        handler = environment.resource_handler.cast()
        # Currently only implemented for Alibaba TechnologyWrapper
        if isinstance(handler, AlibabaResourceHandler):
            wrapper: AlibabaTechnologyWrapper = handler.get_api_wrapper()
            instance_types = wrapper.get_instance_types(zone_id=zone_id)

            instance_type_options = [
                (instance_type, instance_type) for instance_type in instance_types
            ]

            return {
                "options": instance_type_options,
                "override": False,
                "initial_value": initial_value,
            }
