"""
This code takes the selected Enviroment name and performs the import params process
"""
from common.methods import set_progress
from infrastructure.models import Environment


def inbound_web_hook_get(*args, parameters={}, **kwargs):
    aws_env_id = parameters.get("CI_aws_environment_id")
    aws_env = Environment.objects.get(id=aws_env_id)
    importAWSparams_res = ""
    try:
        importAWSparams_res = aws_env.import_parameters()
    except Exception as err:
        importAWSparams_res = err
    set_progress(
        f"This message will show up in CloudBolt's application.log. args: {args}, kwargs: {kwargs}, parameters: {parameters}, importAWSparams_res: {importAWSparams_res}"
    )

    return importAWSparams_res, aws_env_id
