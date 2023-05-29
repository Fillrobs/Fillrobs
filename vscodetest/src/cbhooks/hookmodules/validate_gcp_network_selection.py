"""
Ensure that any selected networks on the GCP order form are available to the selected Zone.
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

    gcp_zone = next(cfv for cfv in cfvs if cfv.field.name == "gcp_zone")
    region = "-".join(gcp_zone.value.split("-", 2)[:2])

    for cfv in cfvs:
        if "sc_nic" in cfv.field.name and cfv.value.name != "default":
            # Region should be populated on all GCPSubnetwork models, fallback to
            # name just in case region is not available (which should no be the case).
            # This is for bug fix: https://cloudbolt.atlassian.net/browse/DEV-18839
            gcp_subnet = cfv.value.cast()
            gcp_subnet_region = getattr(gcp_subnet, "region", None)
            if not gcp_subnet_region:
                gcp_subnet_region = cfv.value.name

            if region not in gcp_subnet_region:
                errors_by_field_id[
                    cfv.field.name
                ] = "The selected subnetwork must be available in the selected zone."

    return errors_by_field_id
