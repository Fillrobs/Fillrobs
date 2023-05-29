from common.methods import set_progress
from infrastructure.models import Environment


def inbound_web_hook_get(*args, parameters={}, **kwargs):
    """
    Use this method for operations that are read-only and do not change anything
    in CloudBolt or the environment.
    """
    azure_envs = Environment.objects.filter(
        resource_handler__resource_technology__modulename__startswith="resourcehandlers.azure"
    )
    # aws_envs = Environment.objects.all()
    azure_env_data = [{"id": env.id, "name": env.name} for env in azure_envs]

    set_progress(
        f"This message will show up in CloudBolt's application.log. args: {args}, kwargs: {kwargs}, parameters: {parameters} envs: {azure_env_data}"
    )
    return azure_env_data
