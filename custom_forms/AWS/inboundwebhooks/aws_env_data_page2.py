"""
This code takes in the selected AWS Environment ID
"""
from common.methods import set_progress
from infrastructure.models import Environment
from accounts.models import Group
from resourcehandlers.models import ResourceHandler
from django.core import serializers


def inbound_web_hook_get(*args, parameters={}, **kwargs):
    aws_env_id = parameters.get("CI_aws_environment_id")
    aws_env = Environment.objects.get(id=aws_env_id)
    aws_env_name = aws_env.name
    rh = aws_env.resource_handler
    rh_name = rh.name
    aws_access_key_id = rh.serviceaccount
    rhc = rh.cast()
    aws_account_id = rhc.account_id
    zones = aws_env.get_cfvs_for_custom_field("aws_availability_zone")
    zones_data = [{"id": zone.id, "name": zone.str_value} for zone in zones]

    elastic_ip = aws_env.get_cfvs_for_custom_field("aws_elastic_ip")
    elastic_ip_data = [{"id": eip.id, "name": eip.str_value} for eip in elastic_ip]

    aws_host = aws_env.get_cfvs_for_custom_field("aws_host")
    aws_host_data = [{"id": ahd.id, "name": ahd.str_value} for ahd in aws_host]

    aws_host_group = aws_env.get_cfvs_for_custom_field("aws_host_group")
    aws_host_group_data = [
        {"id": ahgd.id, "name": ahgd.str_value} for ahgd in aws_host_group
    ]

    delete_ebs_volumes_on_termination = aws_env.get_cfvs_for_custom_field(
        "delete_ebs_volumes_on_termination"
    )
    delete_ebs_vol_term_data = [
        {"id": devt.id, "name": devt.str_value}
        for devt in delete_ebs_volumes_on_termination
    ]

    ebs_volume_types = aws_env.get_cfvs_for_custom_field("ebs_volume_type")
    ebs_volume_type_data = [
        {"id": evtd.id, "name": evtd.str_value} for evtd in ebs_volume_types
    ]

    instance_types = aws_env.get_cfvs_for_custom_field("instance_type")
    sorted_instance_types = sorted(instance_types, key=lambda x: x.str_value)
    instance_type_data = [
        {"id": itd.id, "name": itd.str_value} for itd in sorted_instance_types
    ]

    iops = aws_env.get_cfvs_for_custom_field("iops")
    iops_data = [{"id": iop.id, "name": iop.str_value} for iop in iops]

    key_names = aws_env.get_cfvs_for_custom_field("key_name")
    key_name_data = [
        {"id": key_name.id, "name": key_name.str_value} for key_name in key_names
    ]
    sec_groups = aws_env.get_cfvs_for_custom_field("sec_groups")
    sec_group_data = [
        {"id": sec_group.id, "name": sec_group.str_value} for sec_group in sec_groups
    ]

    # get the AWS Env groups
    aws_env_groups = aws_env.group_set.all()
    aws_env_group_data = []
    aws_env_group_ids = []
    for g in aws_env_groups:
        aws_env_group_data.append((g.id, g.global_id, g.standalone_name))
        # make an Arr of just the ids
        aws_env_group_ids.append(g.id)

    env_networks = aws_env.networks()
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
            if "AWS" in grp.standalone_name:
                grp_id = grp.id
                if grp_id in aws_env_group_ids:
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

    aws_env_data = [
        {
            "awsEnvId": aws_env_id,
            "awsEnvName": f"{aws_env_name}",
            "awsAccessKey": f"{aws_access_key_id}",
            "rhName": f"{rh_name}",
            "awsAccountId": f"{aws_account_id}",
            "zonesData": zones_data,
            "elasticIpData": elastic_ip_data,
            "awsHostData ": aws_host_data,
            "awsHostGroupData": aws_host_group_data,
            "deleteEbsVolTermData": delete_ebs_vol_term_data,
            "ebsVolumeTypeData": ebs_volume_type_data,
            "instanceTypeData": instance_type_data,
            "iopsData": iops_data,
            "keyNameData": key_name_data,
            "secGroupData": sec_group_data,
            "envGroupData": env_group_data,
            "envNetworkData": env_network_data,
        }
    ]

    set_progress(
        f"This message will show up in CloudBolt's application.log. args: {args}, kwargs: {kwargs}, parameters: {parameters}, aws_env_data: {aws_env_data}"
    )
    return aws_env_data
