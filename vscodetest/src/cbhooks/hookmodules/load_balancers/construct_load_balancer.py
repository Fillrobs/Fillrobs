from common.methods import set_progress


def construct_load_balancer(**kwargs):
    members = kwargs.get("members", [])
    ports = kwargs.get("ports")
    lbsi = kwargs.get("lbsi", None)
    resource = kwargs.get("resource")

    if not members:
        return None

    rh = members[0].resource_handler.cast()
    set_progress("Configuring Load Balancing on Resource Handler {}".format(rh))
    rh.create_load_balancer(
        members, resource, lbsi, ports["src_port"], ports["dest_port"],
    )

    return resource.loadbalancer_set.last()
