"""
This code takes in the selected VMware Environment ID
"""
from common.methods import set_progress
from infrastructure.models import Environment
from accounts.models import Group
from orders.models import CustomFieldValue
from resourcehandlers.models import ResourceHandler
from django.core import serializers


def inbound_web_hook_get(*args, parameters={}, **kwargs):
    vmware_env_id = parameters.get("CI_VMware_environment_id")
    vmware_env = Environment.objects.get(id=vmware_env_id)
    vmware_env_name = vmware_env.name
    rh = vmware_env.resource_handler
    rh_name = rh.name

    vmware_datastores = vmware_env.get_cfvs_for_custom_field("vmware_datastore")
    if len(vmware_datastores) == 1:
        vmware_datastores = vmware_env.vmware_datastore
        vmware_datastoresData = [
            {"id": vmware_datastores.id, "name": vmware_datastores.name}
        ]
    else:
        vmware_datastores_Arr = []
        for d in vmware_datastores:
            fid = d.field_id
            e = d.int_value
            fn = CustomFieldValue.objects.get(field_id=fid, int_value=e)
            # print(fn.display_value, fid, e)
            vmware_datastores_Arr.append(
                (fn.id, str(fid) + "|" + str(e) + "|" + str(fn.display_value))
            )
        if len(vmware_datastores_Arr) > 0:
            vmware_datastoresData = [
                {"id": ds[0], "name": str(ds[1])} for ds in vmware_datastores_Arr
            ]

    vmware_disk_types = vmware_env.get_cfvs_for_custom_field("vmware_disk_type")
    vmware_disk_typeData = [
        {"id": vds.id, "name": vds.str_value} for vds in vmware_disk_types
    ]

    # get the vmware Env groups
    vmware_env_groups = vmware_env.group_set.all()
    vmware_env_group_data = []
    vmware_env_group_ids = []
    for g in vmware_env_groups:
        vmware_env_group_data.append((g.id, g.global_id, g.standalone_name))
        # make an Arr of just the ids
        vmware_env_group_ids.append(g.id)

    env_networks = vmware_env.networks()
    if len(env_networks) > 0:
        env_network_data = [{"id": net.id, "name": net.network} for net in env_networks]
    else:
        env_network_data = []

    # we want to get all of the groups and add a field of true if the group is in the env
    # storing all of the groups on the page in a hidden div allows us
    # to use the data to build a dropdown
    all_groups = Group.objects.all()
    env_group_data_arr = []
    if len(all_groups) > 0:
        for grp in all_groups:
            if "VMware" in grp.standalone_name:
                grp_id = grp.id
                if grp_id in vmware_env_group_ids:
                    env_group_data_arr.append((grp_id, grp.standalone_name, True))
                else:
                    env_group_data_arr.append((grp_id, grp.standalone_name, False))
        if len(env_group_data_arr) > 0:
            env_group_data = [
                {"id": env_group[0], "name": env_group[1], "present": env_group[2]}
                for env_group in env_group_data_arr
            ]
        else:
            env_group_data = []
    else:
        env_group_data = []

    # OSBuilds
    os_build_data = [
        {"id": osb.name, "name": osb.name}
        for osb in vmware_env.get_orderable_os_builds()
    ]

    # params
    json_dict = vmware_env.get_cf_values_as_dict()
    env_params_data_arr = []
    c = 0
    for key, value in json_dict.items():
        if "maxis_" in key:
            env_params_data_arr.append(key + ":" + value)
            c = c + 1

    if len(env_params_data_arr) > 0:
        env_params_data = [{"id": epd, "name": epd} for epd in env_params_data_arr]
    else:
        env_params_data = []

    vmware_env_data = [
        {
            "vmwareEnvId": vmware_env_id,
            "vmwareEnvName": f"{vmware_env_name}",
            "rhName": f"{rh_name}",
            "vmwareDatastoresData": vmware_datastoresData,
            "vmwareDiskTypeData": vmware_disk_typeData,
            "envGroupData": env_group_data,
            "envNetworkData": env_network_data,
            "envOSBuildData": os_build_data,
            "envParamsData": env_params_data,
        }
    ]

    set_progress(
        f"This message will show up in CloudBolt's application.log. args: {args}, kwargs: {kwargs}, parameters: {parameters}, vmware_env_data: {vmware_env_data}"
    )
    return vmware_env_data
