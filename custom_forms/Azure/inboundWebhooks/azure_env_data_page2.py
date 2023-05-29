"""
This code takes in the selected Azure Environment ID
"""
from common.methods import set_progress
from infrastructure.models import Environment
from accounts.models import Group
from resourcehandlers.models import ResourceHandler
from django.core import serializers


def inbound_web_hook_get(*args, parameters={}, **kwargs):
    Azure_env_id = parameters.get("CI_Azure_environment_id")
    Azure_env = Environment.objects.get(id=Azure_env_id)
    Azure_env_name = Azure_env.name
    rh = Azure_env.resource_handler
    rh_name = rh.name
    rhc = rh.cast()
    azureServiceAccount = rhc.serviceaccount
    azureClientID = rhc.client_id
    azureTenantID = rhc.azure_tenant_id

    availabilitySetArm = Azure_env.get_cfvs_for_custom_field("availability_set_arm")
    availabilitySetArmData = [
        {"id": asa.id, "name": asa.str_value} for asa in availabilitySetArm
    ]

    availabilityZoneArm = Azure_env.get_cfvs_for_custom_field("availability_zone_arm")
    availabilityZoneArmData = [
        {"id": aza.id, "name": aza.str_value} for aza in availabilityZoneArm
    ]

    createPublicIp = Azure_env.get_cfvs_for_custom_field("create_public_ip")
    createPublicIpData = [
        {"id": cpip.id, "name": cpip.str_value} for cpip in createPublicIp
    ]

    customStorageAccountArm = Azure_env.get_cfvs_for_custom_field(
        "custom_storage_account_arm"
    )
    customStorageAccountArmData = [
        {"id": cstaa.id, "name": cstaa.str_value} for cstaa in customStorageAccountArm
    ]

    enableAcceleratedNetworking = Azure_env.get_cfvs_for_custom_field(
        "enable_accelerated_networking"
    )
    enableAcceleratedNetworkingData = [
        {"id": ean.id, "name": ean.str_value} for ean in enableAcceleratedNetworking
    ]

    nodeSize = Azure_env.get_cfvs_for_custom_field("node_size")
    SortedNodeSize = sorted(nodeSize, key=lambda x: x.str_value)
    nodeSizeData = [{"id": ns.id, "name": ns.str_value} for ns in SortedNodeSize]

    passwordArm = Azure_env.get_cfvs_for_custom_field("password_arm")
    passwordArmData = [{"id": pad.id, "name": pad.str_value} for pad in passwordArm]

    platformFaultDomainCount = Azure_env.get_cfvs_for_custom_field(
        "platform_fault_domain_count"
    )
    platformFaultDomainCountData = [
        {"id": pfdc.id, "name": pfdc.str_value} for pfdc in platformFaultDomainCount
    ]

    resourceGroupArm = Azure_env.get_cfvs_for_custom_field("resource_group_arm")
    resourceGroupArmData = [
        {"id": rga.id, "name": rga.str_value} for rga in resourceGroupArm
    ]
    resourceGroupArmTemplate = Azure_env.get_cfvs_for_custom_field(
        "resource_group_arm_template"
    )
    resourceGroupArmTemplateData = [
        {"id": rgat.id, "name": rgat.str_value} for rgat in resourceGroupArmTemplate
    ]
    storageAccountArm = Azure_env.get_cfvs_for_custom_field("storage_account_arm")
    storageAccountArmData = [
        {"id": saa.id, "name": saa.str_value} for saa in storageAccountArm
    ]

    # get the Azure Env groups
    Azure_env_groups = Azure_env.group_set.all()
    Azure_env_group_data = []
    Azure_env_group_ids = []
    for g in Azure_env_groups:
        Azure_env_group_data.append((g.id, g.global_id, g.standalone_name))
        # make an Arr of just the ids
        Azure_env_group_ids.append(g.id)
    set_progress(f"Azure_env_group_ids = {Azure_env_group_ids}")

    envNetworks = Azure_env.networks()
    if len(envNetworks) > 0:
        envNetworkData = [{"id": net.id, "name": net.network} for net in envNetworks]
    else:
        envNetworkData = []

    # we want to get all of the groups and add a field of true if the group is in the env
    # storing all of the groups on the page in a hidden div allows us
    # to use the data to build a dropdown
    all_groups = Group.objects.all()
    env_group_data_arr = []
    if len(all_groups) > 0:
        for grp in all_groups:
            if "Azure" in grp.standalone_name:
                grp_id = grp.id
                if grp_id in Azure_env_group_ids:
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
    set_progress(f"env_group_data = {env_group_data}")

    # OSBuilds
    os_build_data = [
        {"id": osb.name, "name": osb.name}
        for osb in Azure_env.get_orderable_os_builds()
    ]

    # params
    json_dict = Azure_env.get_cf_values_as_dict()
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

    Azure_env_data = [
        {
            "AzureEnvId": Azure_env_id,
            "azureEnvName": f"{Azure_env_name}",
            "rhName": f"{rh_name}",
            "azureServiceAccount": f"{azureServiceAccount}",
            "azureClientID": f"{azureClientID}",
            "azureTenantID": f"{azureTenantID}",
            "availabilitySetArmData ": availabilitySetArmData,
            "availabilityZoneArmData": availabilityZoneArmData,
            "createPublicIpData": createPublicIpData,
            "customStorageAccountArmData": customStorageAccountArmData,
            "enableAcceleratedNetworkingData": enableAcceleratedNetworkingData,
            "nodeSizeData": nodeSizeData,
            "platformFaultDomainCountData": platformFaultDomainCountData,
            "passwordArmData": passwordArmData,
            "resourceGroupArmData": resourceGroupArmData,
            "resourceGroupArmTemplateData": resourceGroupArmTemplateData,
            "storageAccountArmData": storageAccountArmData,
            "envGroupData": env_group_data,
            "envNetworkData": envNetworkData,
            "envOSBuildData": os_build_data,
            "envParamsData": env_params_data,
        }
    ]

    set_progress(
        f"This message will show up in CloudBolt's application.log. args: {args}, kwargs: {kwargs}, parameters: {parameters}, Azure_env_data: {Azure_env_data}"
    )
    return Azure_env_data
