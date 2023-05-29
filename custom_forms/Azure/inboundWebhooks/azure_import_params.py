"""
This code takes the selected Enviroment name and performs the import params process
"""
from common.methods import set_progress
from infrastructure.models import Environment

def inbound_web_hook_get(*args, parameters={}, **kwargs):
    azure_env_id = parameters.get("CI_Azure_environment_id")
    azure_env = Environment.objects.get(id=azure_env_id)
    importAzureparams_res = ""
    try:
       importAzureparams_res = azure_env.import_parameters() 
    except Exception as err:
        importAzureparams_res = err
    set_progress(
        f"This message will show up in CloudBolt's application.log. args: {args}, kwargs: {kwargs}, parameters: {parameters}, importAzureparams_res: {importAzureparams_res}"
    )

    return importAzureparams_res, azure_env_id