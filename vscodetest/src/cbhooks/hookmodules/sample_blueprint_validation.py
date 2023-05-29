def validate_order_form(blueprint, profile, group, order_data):
    """
    Sample plugin for custom order form validation.

    Args:
        blueprint:  ServiceBlueprint being ordered
        profile:    UserProfile making the order
        group:      Selected Group object
        order_data: Dictionary including data for things like Server Tiers, Actions, and Blueprint-level parameters
    """
    order_form_errors = {}

    # Make this plugin only apply to the "Custom Validation" blueprint
    if blueprint.name != "Custom Validation":
        return {}

    # Validate blueprint parameters
    if "blueprint_params" in order_data:
        bp_params = order_data["blueprint_params"]
        if "group" in bp_params and bp_params["group"].name == "invalid_group_name":
            order_form_errors["blueprint_params"] = "Cannot deploy to this group."

    def validate_fields(item):
        service_item_id = f'{item["service_item"].id}'
        for key, val in item.items():
            if key == "hostname" and len(val) > 12:
                if service_item_id not in order_form_errors:
                    order_form_errors[service_item_id] = {}
                # This nesting under the service_item_id will show the error on the specific form
                # and on the form field itself if it matches the field name (i.e. 'hostname' in this case)
                order_form_errors[service_item_id][
                    "hostname"
                ] = "Hostname longer than 12 characters."
            if key == "meaning_of_life" and val != 42:
                if service_item_id not in order_form_errors:
                    order_form_errors[service_item_id] = {}
                order_form_errors[service_item_id]["meaning_of_life"] = "Invalid value."

    # Validate arbitrary order form values
    # Iterates through all form fields on blueprints and sub-blueprints
    for item_name, item in order_data.items():
        if "formset_data" in item:  # Sub-blueprint form validation
            for sub_bp_item in item["formset_data"]:
                validate_fields(sub_bp_item)
        else:  # Standard form validation
            validate_fields(item)

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

    return order_form_errors
