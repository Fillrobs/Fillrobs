from typing import Union
from common.methods import get_predefined_cfv_from_si
from resourcehandlers.alibaba.alibaba_wrapper import (
    TechnologyWrapper as AlibabaTechnologyWrapper,
)
from resourcehandlers.alibaba.models import AlibabaResourceHandler, AlibabaVSwitch
from resourcehandlers.models import ResourceNetwork
from servicecatalog.models import ServiceItem


def get_options_list(
    field,
    control_value: Union[str, ResourceNetwork] = None,
    service_item: ServiceItem = None,
    **kwargs,
):
    """
    Regenerate options for Alibaba security groups on the order form based on what Nic 1 (aka sc_nic_0) is selected.
    """
    environment = kwargs.get("environment")

    # Abort regeneration if this isn't an Alibaba Environment
    def isEnvForAlibaba(environment):
        return environment and isinstance(
            environment.resource_handler.cast(), AlibabaResourceHandler
        )

    if not isEnvForAlibaba(environment):
        return

    initial_value = get_predefined_cfv_from_si(service_item, environment, field.name)

    # control value may come in as a VSwitch/ResourceNetwork object, or as an id
    if isinstance(control_value, ResourceNetwork):
        cb_switch = control_value.cast()
    else:
        cb_switch_id = control_value
        try:
            cb_switch = AlibabaVSwitch.objects.get(id=cb_switch_id)
        except AlibabaVSwitch.DoesNotExist:
            cb_switch = None
    ali_switch_id = getattr(cb_switch, "network", None)

    security_group_options = []

    if environment and ali_switch_id:
        handler = environment.resource_handler.cast()
        wrapper: AlibabaTechnologyWrapper = handler.get_api_wrapper()
        security_groups = wrapper.get_security_groups_for_switch(ali_switch_id)

        def option_text(sg):
            sg_name = sg.get("SecurityGroupName", None) or "Unnamed Security Group"
            sg_id = sg["SecurityGroupId"]
            return f"{sg_name} ({sg_id})"

        security_group_options = [
            (security_group["SecurityGroupId"], option_text(security_group),)
            for security_group in security_groups
        ]

    return {
        "options": security_group_options,
        "override": False,
        "initial_value": initial_value,
    }
