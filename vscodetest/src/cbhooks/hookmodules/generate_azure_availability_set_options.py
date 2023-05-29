from infrastructure.models import Environment
from servicecatalog.models import ServiceItem  # noqa: F401


def get_options_list(
    field,
    control_value=None,
    form_data=None,
    form_prefix=None,
    service_item=None,
    **kwargs,
):
    """
    Regenerate options for Azure Availability Set on the order form based on what resource group is selected.
    :param field: the availability_set_arm custom field.
    :param kwargs:
    :return options: a list of strings of availability sets by name
    """
    environment = kwargs.get("environment")

    if not environment and form_data:
        environment_key = form_prefix + "-environment"
        environment_id = form_data.get(environment_key, None)
        if isinstance(environment_id, list):
            environment_id = environment_id[0]
        environment = (
            Environment.objects.get(id=int(environment_id)) if environment_id else None
        )

    # initial_value needs to be explicitly set here when loading options for ServiceItemParamsForm
    initial_value = None
    if service_item:
        service_item = service_item.cast()

    if service_item and hasattr(service_item, "get_param_values_predefined_on_si"):
        # Try to get the control_value from predefined fields in the service item
        predefined_control_cfvs = service_item.get_param_values_predefined_on_si(
            environment, field.name
        )
        if predefined_control_cfvs:
            initial_value = predefined_control_cfvs[0].value

    resource_group_name = control_value

    availability_set_options = [
        ("", "No availability set"),
        ("AUTO_CREATE", "Auto-create new availability set"),
    ]

    if environment and resource_group_name:
        handler = environment.resource_handler.cast()
        wrapper = handler.get_api_wrapper()
        availability_set_iterator = wrapper.compute_client.availability_sets.list(
            resource_group_name
        )
        availability_set_options.extend(
            [(a.name, a.name) for a in availability_set_iterator]
        )

    return {
        "options": availability_set_options,
        "override": True,
        "initial_value": initial_value,
    }
