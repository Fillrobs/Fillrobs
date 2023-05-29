"""
In Azure, the Availability Set and Availability Zone parameters are mutually exclusive. Either one can be specified,
but not both. This order validation orchestration hook prevents the order form from being submitted when both are
present, and displays an informative message indicating the issue.
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

    availability_set = next(
        (cfv for cfv in cfvs if cfv.field.name == "availability_set_arm"), None
    )
    availability_zone = next(
        (cfv for cfv in cfvs if cfv.field.name == "availability_zone_arm"), None
    )

    if availability_set and availability_zone:
        errors_by_field_id[availability_set.field.name] = (
            "Availability Sets and Availability Zones are mutually "
            "exclusive. Please provide a value for only one of these "
            "fields."
        )
        errors_by_field_id[availability_zone.field.name] = (
            "Availability Sets and Availability Zones are mutually "
            "exclusive. Please provide a value for only one of these "
            "fields."
        )

    return errors_by_field_id
