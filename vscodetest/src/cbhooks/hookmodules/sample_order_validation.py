def validate_order_form(  # noqa: E302
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
    """
    Sample plugin for custom server tier validation.

    The order form is constructed for the group + env combination, aka "context".
    This includes all parameters that apply to those, as well as hidden parameters.

    Args:
        profile:    UserProfile making the order
        group:      selected group object
        env:        selected environment object
        quantity:   integer if Quantity parameter applies to this context (default 1)
        hostname:   string if hostname field is in the order form (default None)
        cfvs:       list of CustomFieldValue objects (Parameters)
        pcvss:      list of PreconfigurationValueSet objects (Preconfiguration options)
        os_build:   an OSBuild object or None
        build_item: a ServiceItem object or None
    """
    errors_by_field_id = {}

    if hostname == "disallowed-hostname":
        errors_by_field_id["hostname"] = "That hostname is not allowed."

    # Validate arbitrary parameter values
    for cfv in cfvs:
        # Check CustomFieldValue for a particular parameter...
        if cfv.field.name == "meaning_of_life" and cfv.value != 42:
            # For parameter errors, the key must have "cf_" prepended to the parameter name
            errors_by_field_id[
                "cf_meaning_of_life"
            ] = "Nope, try again. {} is not the meaning of life.".format(cfv.value)

    # Preconfigurations
    for pcvs in pcvss:
        # E.g. require appropriate resources for certain orders
        if pcvs.preconfiguration.name == "vm_size":
            if (
                pcvs.value == "small"
                and os_build.os_family.get_base_name() == "Windows"
            ):
                errors_by_field_id[
                    "vm_size"
                ] = "Small is actually not big enough for Windows"

    # Call external systems such as Active Directory services, IP management system, etc.
    # For this, you can use ConnectionInfo objects to store credentials or LDAPUtility for AD
    # queries.
    #
    # Caution: this validation plugin must be performant; a slow response time will degrade your
    # end user's experience while using the order form.
    #
    # Example:
    #     from utilities.models import ConnectionInfo, LDAPUtility
    #     ci = ConnectionInfo.objects.get(name='Some Service')
    # or
    #     ad = LDAPUtility.objects.get(ldap_domain='mydomain.com')

    return errors_by_field_id
