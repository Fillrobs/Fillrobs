"""
This code takes the values from the AWS Environment form
"""
from common.methods import set_progress
from infrastructure.models import CustomField, Environment
from orders.models import CustomFieldValue


def process_form_field(aws_env, formInputName, formData, current_data_types):
    try:
        formDataInput = formData.strip("[]").split(", ")

        formData = [int(x) for x in formDataInput]
        set_progress(f"formData={formData}")

        if (
            isinstance(formData, list)
            and len(formData) > 0
            and len(current_data_types) > 0
        ):
            # loop through current_inst_types and if not in formInstanceTypeData then delete the CustomFieldValue matching the id
            for cfo in current_data_types:
                if int(cfo.id) not in formData:
                    cfo_obj = CustomFieldValue.objects.get(id=cfo.id).delete()
                else:
                    set_progress(
                        f"{formInputName} {cfo.str_value} added to the AWS Environment"
                    )

        if isinstance(formData, list) and len(formData) == 0:
            set_progress(f"clearing {formInputName} from the AWS Environment")
            aws_env.clear_cfv(formInputName)
        return True
    except Exception as e:
        set_progress(f"Error clearing {formInputName} error={e}")
        return False


def run(job, *args, **kwargs):
    aws_env_id = "{{ CI_aws_environment_id}}"
    set_progress(f"AWS Env ID = {aws_env_id}")
    aws_env = Environment.objects.get(id=aws_env_id)
    # we need them all imported and then remove as per the fields - but the Id's change
    # aws_env.import_parameters()
    formEnvNameInput = "{{ CI_awsEnvName }}"
    aws_env.name = formEnvNameInput
    aws_env.save()

    zonesDataInput = "{{CI_zonesData}}"
    set_progress(f"zonesDataInput = {zonesDataInput}")
    current_zones = aws_env.get_cfvs_for_custom_field("aws_availability_zone")
    current_zones_res = process_form_field(
        aws_env, "aws_availability_zone", zonesDataInput, current_zones
    )

    # get the data from the form
    formInstanceTypeDataInput = "{{ CI_instanceTypeData }}"
    set_progress(f"formInstanceTypeDataInput={formInstanceTypeDataInput}")
    # now loop through the imported fields and if the id is within the form data keep if not delete
    current_inst_types = aws_env.get_cfvs_for_custom_field("instance_type")
    instance_type_res = process_form_field(
        aws_env, "instance_type", formInstanceTypeDataInput, current_inst_types
    )

    formElasticIpDataInput = "{{ CI_elasticIpData }}"
    set_progress(f"formElasticIpDataInput={formElasticIpDataInput}")
    current_ElasticIp_types = aws_env.get_cfvs_for_custom_field("aws_elastic_ip")
    ElasticIp_res = process_form_field(
        aws_env, "aws_elastic_ip", formElasticIpDataInput, current_ElasticIp_types
    )

    formAwsHostDataInput = "{{ CI_awsHostData }}"
    set_progress(f"formAwsHostDataInput={formAwsHostDataInput}")
    current_AwsHostData = aws_env.get_cfvs_for_custom_field("aws_host")
    AwsHostData_res = process_form_field(
        aws_env, "aws_host", formAwsHostDataInput, current_AwsHostData
    )

    formAwsHostGroupDataInput = "{{ CI_awsHostGroupData }}"
    set_progress(f"formAwsHostGroupDataInput={formAwsHostGroupDataInput}")
    current_AwsHostGroupData = aws_env.get_cfvs_for_custom_field("aws_host_group")
    AwsHostGroupData_res = process_form_field(
        aws_env, "aws_host_group", formAwsHostGroupDataInput, current_AwsHostGroupData
    )

    formDeleteEbsVolTermInput = "{{ CI_deleteEbsVolTermData }}"
    set_progress(f"formDeleteEbsVolTermInput={formDeleteEbsVolTermInput}")
    current_DeleteEbsVolTerm_types = aws_env.get_cfvs_for_custom_field(
        "delete_ebs_volumes_on_termination"
    )
    DeleteEbsVolTerm_res = process_form_field(
        aws_env,
        "delete_ebs_volumes_on_termination",
        formDeleteEbsVolTermInput,
        current_DeleteEbsVolTerm_types,
    )

    formEbsVolumeTypeInput = "{{ CI_ebsVolumeTypeData }}"
    set_progress(f"formEbsVolumeTypeInput={formEbsVolumeTypeInput}")
    current_EbsVolumeType_types = aws_env.get_cfvs_for_custom_field("ebs_volume_type")
    EbsVolumeType_res = process_form_field(
        aws_env, "ebs_volume_type", formEbsVolumeTypeInput, current_EbsVolumeType_types
    )

    formIopsDataInput = "{{ CI_iopsData }}"
    set_progress(f"formIopsDataInput={formIopsDataInput}")
    current_IopsData_types = aws_env.get_cfvs_for_custom_field("iops")
    IopsData_res = process_form_field(
        aws_env, "iops", formIopsDataInput, current_IopsData_types
    )

    formKeyNameDataInput = "{{ CI_keyNameData }}"
    set_progress(f"formKeyNameDataInput={formKeyNameDataInput}")
    current_KeyNameData_types = aws_env.get_cfvs_for_custom_field("key_name")
    KeyNameData_res = process_form_field(
        aws_env, "key_name", formKeyNameDataInput, current_KeyNameData_types
    )

    formSecGroupDataInput = "{{ CI_secGroupData }}"
    set_progress(f"formSecGroupDataInput={formSecGroupDataInput}")
    current_SecGroupData_types = aws_env.get_cfvs_for_custom_field("sec_groups")
    SecGroupData_res = process_form_field(
        aws_env, "sec_groups", current_SecGroupData_types, current_SecGroupData_types
    )

    formNetworkDataInput = "{{ CI_envNetworkData }}"
    formDataInput = formNetworkDataInput.strip("[]").split(", ")

    # set_progress(f"2)formNetworkDataInput=" + formNetworkDataInput)
    current_Networks = aws_env.get_possible_networks()
    for n in current_Networks:
        netid = n.id
        set_progress(f"netid={netid}")
        fNetId = False
        for f in formDataInput:
            set_progress(f"found {f}")
            if int(f) == int(netid):
                fNetId = True
                set_progress(f"keeping network id {netid}")
                break
        if fNetId == False:
            set_progress(f"removing network id {netid} from the Environment")
            n.delete()
    # aws_env.import_parameters() # reset to default
    # get the value  aws_env.get_value_for_custom_field("aws_availability_zone")
    # get the values  aws_env.get_cfvs_for_custom_field("aws_availability_zone")
    # aws_env.set_value_for_custom_field("aws_availability_zone", value="ap-southeast-1b")
    # aws_env.get_cfvs_for_custom_field("instance_type")
    # aws_env.set_value_for_custom_field("instance_type", value="t2.nano,t3.nano")

    """   
        "elasticIpData",
        "awsHostData",
        "awsHostGroupData",
        "deleteEbsVolTermData",
        "ebsVolumeTypeData",
        "instanceTypeData",
        "iopsData",
        "keyNameData",
        "secGroupData",
      ]
    """

    return "SUCCESS", "AWS Env Selected", ""
