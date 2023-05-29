"""
This code takes the values from the VMware Environment form
"""
from common.methods import set_progress
from infrastructure.models import CustomField, Environment
from orders.models import CustomFieldValue


def process_form_field(VMware_env, formInputName, formData, current_data_types):
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
                        f"{formInputName} {cfo.str_value} added to the VMware Environment"
                    )

        if isinstance(formData, list) and len(formData) == 0:
            set_progress(f"clearing {formInputName} from the VMware Environment")
            VMware_env.clear_cfv(formInputName)
        return True
    except Exception as e:
        set_progress(f"Error clearing {formInputName} error={e}")
        return False


def run(job, *args, **kwargs):
    VMware_env_id = "{{ CI_VMware_environment_id}}"
    set_progress(f"VMware Env ID = {VMware_env_id}")
    VMware_env = Environment.objects.get(id=VMware_env_id)
    # we need them all imported and then remove as per the fields - but the Id's change
    # VMware_env.import_parameters()
    formEnvNameInput = "{{ CI_vmwareEnvName }}"
    VMware_env.name = formEnvNameInput
    VMware_env.save()

    formVmwareDatastoresInput = "{{CI_vmwareDatastoresData}}"
    set_progress(
        f"formVmwareDatastoresInput = {formVmwareDatastoresInput} {len(formVmwareDatastoresInput)}"
    )
    # current_datastores = VMware_env.vmware_datastore
    # set_progress(f"vmware_datastore {formVmwareDatastoresInput}, {current_datastores}")
    # datastores are stored with the CustomFieldValue ID as the identifier
    # the name consists of the field_id | int_val display_value
    if len(formVmwareDatastoresInput) > 0:
        current_ds = VMware_env.get_cfvs_for_custom_field("vmware_datastore")
        vmware_datastores_Arr = []
        for d in current_ds:
            fid = d.field_id
            e = d.int_value
            fn = CustomFieldValue.objects.get(field_id=fid, int_value=e)
            # print(fn.display_value, fid, e)
            if str(fn.id) not in formVmwareDatastoresInput:
                # vmware_datastores_Arr.append((fn.id, str(fid)+"|"+str(e)+"|"+ str(fn.display_value)))
                set_progress(f"Deleting datastore with id={fn.id}")
                fn.delete()

            # vmware datastores are stored differently to other fields
            # current_datastores_res = process_form_field(
            #            VMware_env,
            #            "vmware_datastore",
            #            formVmwareDatastoresInput,
            #            current_datastores,
            #        )

    else:
        set_progress("Clearing VMware Datastores")
        VMware_env.vmware_datastore = None
        VMware_env.save()

    # get the data from the form
    formvmwareDiskTypeDataInput = "{{ CI_vmwareDiskTypeData }}"
    set_progress(f"formvmwareDiskTypeDataInput={formvmwareDiskTypeDataInput}")
    # now loop through the imported fields and if the id is within the form data keep if not delete
    current_disk_types = VMware_env.get_cfvs_for_custom_field("vmware_disk_type")
    current_disk_types_res = process_form_field(
        VMware_env, "vmware_disk_type", formvmwareDiskTypeDataInput, current_disk_types
    )

    # VMware_env.import_parameters() # reset to default
    # get the value  VMware_env.get_value_for_custom_field("VMware_availability_zone")
    # get the values  VMware_env.get_cfvs_for_custom_field("VMware_availability_zone")
    # VMware_env.set_value_for_custom_field("VMware_availability_zone", value="ap-southeast-1b")
    # VMware_env.get_cfvs_for_custom_field("instance_type")
    # VMware_env.set_value_for_custom_field("instance_type", value="t2.nano,t3.nano")

    return "SUCCESS", "VMware Env Selected", ""
