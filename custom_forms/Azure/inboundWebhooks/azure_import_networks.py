"""
This code takes the selected Enviroment name and performs the import networks process
"""
from common.methods import set_progress
from infrastructure.models import Environment


def inbound_web_hook_get(*args, parameters={}, **kwargs):
    azure_env_id = parameters.get("CI_Azure_environment_id")
    azure_env = Environment.objects.get(id=azure_env_id)
    importAzurenetworks_res = ""
    try:
        handler = azure_env.resource_handler.cast()
        importAzurenetworks_res = handler.sync_subnets(azure_env)

    except Exception as err:
        importAzurenetworks_res = err
    set_progress(
        f"This message will show up in CloudBolt's application.log. args: {args}, kwargs: {kwargs}, parameters: {parameters}, importAzurenetworks_res: {importAzurenetworks_res}"
    )

    return importAzurenetworks_res, azure_env_id
