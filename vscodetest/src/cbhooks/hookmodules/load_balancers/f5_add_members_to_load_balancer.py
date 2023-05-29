from common.methods import set_progress


def add_members_to_load_balancer(**kwargs):

    # get common construct attributes
    lb = kwargs.get("lb")
    members = kwargs.get("members", [])

    big = lb.get_bigsuds_connection()
    pm_list = []

    for m in members:
        # add to pool members list
        set_progress("Adding pool member: {}".format(m.hostname))
        pm_list.append({"address": m.ip, "port": lb.destination_port})

    big.LocalLB.Pool.add_member_v2([lb.pool_identifier], [pm_list])
