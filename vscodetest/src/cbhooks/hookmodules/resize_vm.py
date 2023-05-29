"""A CB Hook Module to resize an Azure VM"""
import json


def run(job, logger=None, *args, **kwargs):
    """
    Resize the VM
    """
    new_size = "{{ new_size }}"
    if new_size is None:
        return "FAILURE", "", "ERROR, did not receive a new size"

    server = kwargs.get("server", None)
    if server is None:
        return (
            "FAILURE",
            "",
            "This plugin only runs against a Server, no Server object given",
        )

    rh = server.resource_handler.cast()
    updated_server_record = rh.resize_server(server, new_size)
    if updated_server_record.hardware_profile.vm_size != new_size:
        return (
            "FAILURE",
            "",
            "After calling Azure, server size is {}, though we requested {}".format(
                updated_server_record.hardware_profile.vm_size, new_size
            ),
        )
    logger.debug(
        "updated server_details:\n{}".format(
            json.dumps(updated_server_record.as_dict(), indent=4)
        )
    )
    # Update value of Node Size parameter on the server in CB Database.
    server.set_value_for_custom_field("node_size", new_size)
    server.save()
    server.refresh_info()
    return (
        "SUCCESS",
        "VM size updated in Azure to {}".format(
            updated_server_record.hardware_profile.vm_size
        ),
        "",
    )


def generate_options_for_new_size(*args, **kwargs):
    """
    Get all Azure environments configured for this blueprint.
    """
    server = kwargs.get("server", None)
    if server:
        rh = server.resource_handler.cast()
        return rh.get_available_sizes_for_server(server, exclude_current_size=True)
    return None
