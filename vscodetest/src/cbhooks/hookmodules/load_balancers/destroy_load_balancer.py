from common.methods import set_progress


def destroy_load_balancer(**kwargs):

    # get common construct attributes
    lb = kwargs.get("lb")

    if lb.resource_handler:
        rh = lb.resource_handler.cast()
        set_progress("Destroying load balancer on Resource Handler {}".format(rh))
        rh.delete_load_balancer(lb)
