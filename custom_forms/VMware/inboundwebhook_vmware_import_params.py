"""
This code takes the selected Enviroment name and performs the import params process
"""
from common.methods import set_progress
from infrastructure.models import Environment


def inbound_web_hook_get(*args, parameters={}, **kwargs):
    vmware_env_id = parameters.get("CI_vmware_environment_id")
    vmware_env = Environment.objects.get(id=vmware_env_id)
    importVMwareparams_res = ""
    try:
        importVMwareparams_res = vmware_env.import_parameters()
    except Exception as err:
        importVMwareparams_res = err
    set_progress(
        f"This message will show up in CloudBolt's application.log. args: {args}, kwargs: {kwargs}, parameters: {parameters}, importAWSparams_res: {importVMwareparams_res}"
    )

    return importVMwareparams_res, vmware_env_id
