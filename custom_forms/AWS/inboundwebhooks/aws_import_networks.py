"""
This code takes the selected Enviroment name and performs the import networks process
"""
from common.methods import set_progress
from infrastructure.models import Environment


def inbound_web_hook_get(*args, parameters={}, **kwargs):
    aws_env_id = parameters.get("CI_aws_environment_id")
    aws_env = Environment.objects.get(id=aws_env_id)
    importAWSnetworks_res = ""
    try:
        handler = aws_env.resource_handler.cast()
        importAWSnetworks_res = handler.sync_subnets(aws_env)

    except Exception as err:
        importAWSnetworks_res = err
    set_progress(
        f"This message will show up in CloudBolt's application.log. args: {args}, kwargs: {kwargs}, parameters: {parameters}, importAWSnetworks_res: {importAWSnetworks_res}"
    )

    return importAWSnetworks_res, aws_env_id
