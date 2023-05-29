# given an environment and group, this action will return the intersection of
# group and environment network options instead of the union.


def get_options_list(field, environment=None, group=None, **kwargs):

    if field.name.startswith("sc_nic_") and not field.name.endswith("ip"):
        # if this is a NIC network field return the intersection of group and env
        # instead of the union
        net_options = set(environment.custom_field_options.filter(field=field).all())
        if group:
            net_options = net_options.intersection(
                group.custom_field_options.filter(field=field).all()
            )

        ret_list = []
        for net_cfv in net_options:
            # when using generated options on networks, you must return a list of network CFVs.
            # a tuple of (net_cfv, net_cfv) will automatically be created for each option even though only the object
            # is appended. If you choose to create a tuple, the first item must be the net_cfv, the second item will
            # not be used
            ret_list.append(net_cfv)

        return ret_list

    return []
