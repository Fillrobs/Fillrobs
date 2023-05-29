"""
This code takes in the group_id and CMP Environment ID and removes the Group from the ENV 
"""
from common.methods import set_progress
from infrastructure.models import Environment


def inbound_web_hook_get(*args, parameters={}, **kwargs):
    group_id = parameters.get("group_id")
    env_id = parameters.get("EnvID")
    env = Environment.objects.get(id=env_id)
    removeGroupEnv_res = "Success"
    try:
        env.group_set.remove(group_id)
        set_progress(
            f"Deletion of group_id = {group_id} from  env_id = {env_id} {removeGroupEnv_res}"
        )
    except Exception as err:
        removeGroupEnv_res = err
        return False
        set_progress(
            f"Deletion of group_id = {group_id} from  env_id = {env_id} {removeGroupEnv_res}"
        )
    return True
