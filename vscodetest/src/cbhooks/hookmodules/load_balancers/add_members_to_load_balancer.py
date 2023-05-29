from common.methods import set_progress


def add_members_to_load_balancer(**kwargs):

    # get common construct attributes
    lb = kwargs.get("lb")
    members = kwargs.get("members", [])

    if not members:
        return None

    rh = lb.resource_handler.cast()
    set_progress("Adding members to load balancer on Resource Handler {}".format(rh))
    rh.add_servers_to_load_balancer(lb, members)
