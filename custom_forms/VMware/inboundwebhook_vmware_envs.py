from common.methods import set_progress
from infrastructure.models import Environment


def inbound_web_hook_get(*args, parameters={}, **kwargs):
    """
    Use this method for operations that are read-only and do not change anything
    in CloudBolt or the environment.
    """
    vmware_envs = Environment.objects.filter(
        resource_handler__resource_technology__modulename__startswith="resourcehandlers.vmware"
    )
    vmware_env_data = [{"id": env.id, "name": env.name} for env in vmware_envs]

    set_progress(
        f"This message will show up in CloudBolt's application.log. args: {args}, kwargs: {kwargs}, parameters: {parameters} envs: {vmware_env_data}"
    )
    return vmware_env_data
