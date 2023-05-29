"""
This code takes in a Group ID and Environment ID and adds the group to the env
"""
from common.methods import set_progress
from infrastructure.models import Environment


def inbound_web_hook_get(*args, parameters={}, **kwargs):
    group_id = parameters.get("group_id")
    env_id = parameters.get("EnvID")
    env = Environment.objects.get(id=env_id)
    addGroupEnv_res = "Success"
    try:
        env.group_set.add(group_id)
    except Exception as err:
        addGroupEnv_res = err
        return False
    set_progress(f"group_id = {group_id} added to env_id = {env_id} {addGroupEnv_res}")
    return True
