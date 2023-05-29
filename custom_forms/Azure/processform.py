"""
This code takes the values from the Azure Environment form
"""
from common.methods import set_progress
from infrastructure.models import CustomField, Environment
from orders.models import CustomFieldValue


def process_form_field(Azure_env, formInputName, formData, current_data_types):
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
                        f"{formInputName} {cfo.str_value} added to the Azure Environment"
                    )

        if isinstance(formData, list) and len(formData) == 0:
            set_progress(f"clearing {formInputName} from the Azure Environment")
            Azure_env.clear_cfv(formInputName)
        return True
    except Exception as e:
        set_progress(f"Error clearing {formInputName} error={e}")
        return False


def run(job, *args, **kwargs):
    Azure_env_id = "{{ CI_Azure_environment_id}}"
    set_progress(f"Azure Env ID = {Azure_env_id}")
    Azure_env = Environment.objects.get(id=Azure_env_id)
    # we need them all imported and then remove as per the fields - but the Id's change
    # Azure_env.import_parameters()
    formEnvNameInput = "{{ CI_azureEnvName }}"
    Azure_env.name = formEnvNameInput
    Azure_env.save()

    formavailabilitySetArmInput = "{{CI_availabilitySetArm}}"
    set_progress(f"formavailabilitySetArmInput = {formavailabilitySetArmInput}")
    current_availabilitySetArm = Azure_env.get_cfvs_for_custom_field(
        "availability_set_arm"
    )
    current_availabilitySetArm_res = process_form_field(
        Azure_env,
        "availability_set_arm",
        formavailabilitySetArmInput,
        current_availabilitySetArm,
    )

    # get the data from the form
    formavailabilityZoneArmInput = "{{ CI_availabilityZoneArma }}"
    set_progress(f"formavailabilityZoneArmInput={formavailabilityZoneArmInput}")
    # now loop through the imported fields and if the id is within the form data keep if not delete
    current_availabilityZoneArm = Azure_env.get_cfvs_for_custom_field(
        "availability_zone_arm"
    )
    availabilityZoneArm_res = process_form_field(
        Azure_env,
        "availability_zone_arm",
        formavailabilityZoneArmInput,
        current_availabilityZoneArm,
    )

    formCreatePublicIpInput = "{{ CI_createPublicIp }}"
    set_progress(f"formCreatePublicIpInput={formCreatePublicIpInput}")
    current_CreatePublicIp = Azure_env.get_cfvs_for_custom_field("create_public_ip")
    CreatePublicIp_res = process_form_field(
        Azure_env, "create_public_ip", formCreatePublicIpInput, current_CreatePublicIp
    )

    formCustomStorageAccountArmInput = "{{ CI_customStorageAccountArm }}"
    set_progress(f"formCustomStorageAccountArmInput={formCustomStorageAccountArmInput}")
    current_customStorageAccountArm = Azure_env.get_cfvs_for_custom_field(
        "custom_storage_account_arm"
    )
    customStorageAccountArm_res = process_form_field(
        Azure_env,
        "custom_storage_account_arm",
        formCustomStorageAccountArmInput,
        current_customStorageAccountArm,
    )

    formEnableAcceleratedNetworkingInput = "{{ CI_azureHostGroupData }}"
    set_progress(
        f"formEnableAcceleratedNetworkingInput={formEnableAcceleratedNetworkingInput}"
    )
    current_EnableAcceleratedNetworking = Azure_env.get_cfvs_for_custom_field(
        "enable_accelerated_networking"
    )
    EnableAcceleratedNetworking_res = process_form_field(
        Azure_env,
        "enable_accelerated_networking",
        formEnableAcceleratedNetworkingInput,
        current_EnableAcceleratedNetworking,
    )

    formNodeSizeInput = "{{ CI_nodeSize }}"
    set_progress(f"formNodeSizeInput={formNodeSizeInput}")
    current_NodeSize = Azure_env.get_cfvs_for_custom_field("node_size")
    NodeSize_res = process_form_field(
        Azure_env, "node_size", formNodeSizeInput, current_NodeSize
    )

    formPasswordArmInput = "{{ CI_passwordArm }}"
    set_progress(f"formPasswordArmInput={formPasswordArmInput}")
    current_PasswordArm = Azure_env.get_cfvs_for_custom_field("password_arm")
    PasswordArm_res = process_form_field(
        Azure_env,
        "password_arm",
        formPasswordArmInput,
        current_PasswordArm,
    )

    formplatformFaultDomainCountInput = "{{ CI_platformFaultDomainCount }}"
    set_progress(
        f"formplatformFaultDomainCountInput={formplatformFaultDomainCountInput}"
    )
    current_platformFaultDomainCount = Azure_env.get_cfvs_for_custom_field(
        "platform_fault_domain_count"
    )
    platformFaultDomainCount_res = process_form_field(
        Azure_env,
        "platform_fault_domain_count",
        formplatformFaultDomainCountInput,
        current_platformFaultDomainCount,
    )

    formResourceGroupArmInput = "{{ CI_resourceGroupArm }}"
    set_progress(f"formResourceGroupArmInput={formResourceGroupArmInput}")
    current_ResourceGroupArm = Azure_env.get_cfvs_for_custom_field("resource_group_arm")
    ResourceGroupArm_res = process_form_field(
        Azure_env,
        "resource_group_arm",
        formResourceGroupArmInput,
        current_ResourceGroupArm,
    )

    formResourceGroupArmTemplateInput = "{{ CI_resourceGroupArmTemplate }}"
    set_progress(
        f"formResourceGroupArmTemplateInput={formResourceGroupArmTemplateInput}"
    )
    current_ResourceGroupArmTemplate = Azure_env.get_cfvs_for_custom_field(
        "resource_group_arm_template"
    )
    ResourceGroupArmTemplate_res = process_form_field(
        Azure_env,
        "resource_group_arm_template",
        formResourceGroupArmTemplateInput,
        current_ResourceGroupArmTemplate,
    )

    formStorageAccountArmInput = "{{ CI_storageAccountArm }}"
    set_progress(f"formStorageAccountArmInput={formStorageAccountArmInput}")
    current_StorageAccountArm = Azure_env.get_cfvs_for_custom_field(
        "storage_account_arm"
    )
    StorageAccountArm_res = process_form_field(
        Azure_env,
        "storage_account_arm",
        formStorageAccountArmInput,
        current_StorageAccountArm,
    )

    # Azure_env.import_parameters() # reset to default
    # get the value  Azure_env.get_value_for_custom_field("Azure_availability_zone")
    # get the values  Azure_env.get_cfvs_for_custom_field("Azure_availability_zone")
    # Azure_env.set_value_for_custom_field("Azure_availability_zone", value="ap-southeast-1b")
    # Azure_env.get_cfvs_for_custom_field("instance_type")
    # Azure_env.set_value_for_custom_field("instance_type", value="t2.nano,t3.nano")

    """   
       "availabilitySetArmData",
        "availabilityZoneArmData",
        "createPublicIpData",
        "customStorageAccountArmData",
        "enableAcceleratedNetworkingData",
        "nodeSizedata",
        "platformFaultDomainCountData",
        "passwordArmData",
        "resourceGroupArmData",
        "resourceGroupArmTemplateData",
        "storageAccountArmData",
        "envGroupData",
        "envNetworkData",
    """

    return "SUCCESS", "Azure Env Selected", ""
