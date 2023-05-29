"""
In Azure, when a user orders a server using an auto-created custom
storage account, the storage account types that can be selected are
limited. This ensures that, of the types we offer, a valid one is
selected.
"""


def validate_order_form(
    profile,
    group,
    env,
    quantity,
    hostname,
    cfvs,
    pcvss,
    os_build=None,
    build_item=None,
    **kwargs,
):
    errors_by_field_id = {}
    use_custom_storage_acount = next(
        (cfv for cfv in cfvs if cfv.field.name == "custom_storage_account_arm"), None
    )
    storage_account = next(
        (cfv for cfv in cfvs if cfv.field.name == "storage_account_arm"), None
    )
    if use_custom_storage_acount and not storage_account:
        valid_storage_account_types = ["Standard_LRS", "Premium_LRS"]
        storage_account_type = next(
            (cfv for cfv in cfvs if cfv.field.name == "storage_account_type_arm"), None
        )
        if (
            storage_account_type
            and storage_account_type.str_value not in valid_storage_account_types
        ):
            valid_types_str = ", ".join(valid_storage_account_types)
            errors_by_field_id[
                "storage_account_type_arm"
            ] = f"Auto-created custom storage accounts may only use the following storage types: {valid_types_str}"

    return errors_by_field_id
