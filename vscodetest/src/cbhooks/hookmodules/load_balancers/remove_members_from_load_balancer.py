from common.methods import set_progress


def remove_members_from_load_balancer(**kwargs):

    # get common construct attributes
    lb = kwargs.get("lb")
    members = kwargs.get("members", [])

    if not members:
        return None

    if lb.resource_handler:
        rh = lb.resource_handler.cast()
        set_progress(
            "Removing members from load balancer on Resource Handler {}".format(rh)
        )
        rh.remove_servers_from_load_balancer(lb, members)
