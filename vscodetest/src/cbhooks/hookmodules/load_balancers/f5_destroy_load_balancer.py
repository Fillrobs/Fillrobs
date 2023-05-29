from common.methods import set_progress


def delete_virtual_server(b, virtualname):
    path = "/Common/{}".format(virtualname)
    if path in b.LocalLB.VirtualServer.get_list():
        b.LocalLB.VirtualServer.delete_virtual_server([virtualname])
        set_progress("Successfully deleted Virtual Server '{}'".format(virtualname))
    else:
        set_progress("Virtual Server '{}' not found".format(virtualname))


def delete_pool(b, pool_name):
    if pool_name in b.LocalLB.Pool.get_list():
        b.LocalLB.Pool.delete_pool([pool_name])
        set_progress("Successfully deleted Pool '{}'".format(pool_name))
    else:
        set_progress("Pool '{}' not found.".format(pool_name))


def destroy_load_balancer(**kwargs):

    lb = kwargs.get("lb")

    big = lb.get_bigsuds_connection()

    set_progress("Deleting member servers")
    if lb.servers.all():
        lb.remove_servers(lb.servers.all())

    # functional process to delete load balancer in F5
    set_progress("Deleting virtual server and pool")
    delete_virtual_server(big, lb.identifier)
    delete_pool(big, lb.pool_identifier)
