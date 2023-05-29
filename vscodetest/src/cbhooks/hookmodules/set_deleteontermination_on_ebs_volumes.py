"""
A hook to modify the EBS Volumes 'deleteOnTermination' attribute whenever the OOTB CB parameter
delete_ebs_volumes_on_termination is modified on the server.
"""
from utilities.logger import ThreadLogger

logger = ThreadLogger(__name__)


def run(server=None, new_value=None):
    """
    Connects to the boto client to modify the EBS volumes deleteOnTermination value based on the new param value.

    :param server: the AWS server object.
    :param new_value: the new custom field value
    """
    if not server:
        return

    instance_id = server.ec2serverinfo.instance_id

    if new_value:
        logger.info(
            "Parameter 'Auto-delete EBS Volumes on Termination' is set to {}.".format(
                new_value,
            )
        )

        rh = server.resource_handler.cast()
        region = server.ec2serverinfo.ec2_region
        wrapper = rh.get_api_wrapper(region_name=region)

        # the new_value is sometimes a string. Convert it to a boolean.
        str_to_bool = {"True": True, "False": False}
        if type(new_value) == str:
            new_value = str_to_bool.get(new_value)

        wrapper.set_ebs_volumes_delete_on_termination(
            server_name=server.hostname, instance_id=instance_id, value=new_value
        )
        output = "Set deleteOnTermination to {} for EBS volumes on CB server: {}.".format(
            new_value, server
        )

    else:  # the field is being deleted from the server. the value will stay the same in AWS.
        output = (
            "No new value given for parameter 'Auto-Delete EBS Volumes on Termination'. "
            "Will not modify any AWS EBS Volumes"
        )

    status, errors = "SUCCESS", ""
    return status, output, errors
