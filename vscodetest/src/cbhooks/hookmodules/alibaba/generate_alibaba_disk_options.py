from common.methods import get_predefined_cfv_from_si
from resourcehandlers.alibaba.alibaba_wrapper import (
    TechnologyWrapper as AlibabaTechnologyWrapper,
)


def get_options_list(
    field, control_value=None, service_item=None, **kwargs,
):
    """
    Regenerate options for Alibaba disk types on the order form based on what instance type is selected.
    """
    environment = kwargs.get("environment")

    initial_value = get_predefined_cfv_from_si(service_item, environment, field.name)

    instance_type = control_value

    disk_options = []

    display_names = {
        "cloud_essd": "Enhanced SSD",
        "cloud_ssd": "Standard SSD",
        "cloud_efficiency": "Ultra Disk",
        "cloud": "Basic Disk",
    }

    if environment and instance_type:
        handler = environment.resource_handler.cast()
        wrapper: AlibabaTechnologyWrapper = handler.get_api_wrapper()
        disk_types = wrapper.get_disk_types_for_instance_type(instance_type)

        disk_options = [(disk, display_names.get(disk, disk)) for disk in disk_types]

    return {
        "options": disk_options,
        "override": False,
        "initial_value": initial_value,
    }
