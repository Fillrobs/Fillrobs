from common.methods import set_progress
from loadbalancers.models import LoadBalancerAppliance
from networks.models import F5LoadBalancer

# HA Proxy specific inputs
LB_METHOD = "{{ lb_method }}"
virtual_server_name_template = "{{ virtual_server_name_template }}"
f5_appliance_id = "{{ f5_appliance }}"


def generate_options_for_f5_appliance(**kwargs):
    """
    Returns a list of LB Method choices to be used in F5 Load Balancers.
    """
    f5_appliances = LoadBalancerAppliance.objects.filter(technology__type_slug="f5")
    f5_options = [(f5.id, f5.name) for f5 in f5_appliances]
    return f5_options


def generate_options_for_lb_method(**kwargs):
    """
    Returns a list of LB Method choices to be used in F5 Load Balancers.
    """
    return [
        ("LB_METHOD_LEAST_SESSIONS", "Least Sessions"),
        ("LB_METHOD_ROUND_ROBIN", "Round Robin"),
        ("LB_METHOD_RATIO_MEMBER", "Ratio Member"),
        ("LB_METHOD_LEAST_CONNECTION_MEMBER", "Least Connection Member"),
        ("LB_METHOD_FASTEST_NODE_ADDRESS", "Fastest Node Address"),
        ("LB_METHOD_PREDICTIVE_NODE_ADDRESS", "Predictive Node Address"),
        ("LB_METHOD_DYNAMIC_RATIO_MEMBER", "Dynamic Ratio Member"),
        (
            "LB_METHOD_WEIGHTED_LEAST_CONNECTION_MEMBER",
            "Weighted Least Connection Member",
        ),
        ("LB_METHOD_RATIO_SESSION", "Ratio Session"),
        ("LB_METHOD_RATIO_LEAST_CONNECTION_MEMBER", "Ratio Least Connection Member"),
    ]


def create_pool(b, pool_name, lb_method, destination_port):
    """
    Wrapper method to bigsuds.BIGIP(**connection).LocalLB.Pool methods
    """
    b.LocalLB.Pool.create_v2([pool_name], [lb_method], [[]])
    # set required health monitor on pool, profile used http
    b.LocalLB.Pool.set_monitor_association(
        monitor_associations=[
            {
                "monitor_rule": {
                    "monitor_templates": ["/Common/http"],
                    "quorum": 0,
                    "type": "MONITOR_RULE_TYPE_SINGLE",
                },
                "pool_name": pool_name,
            }
        ]
    )


def create_virtual_server(b, virtual_name, address, source_port, pool_name):
    """
    Wrapper method to bigsuds.BIGIP(**connection).LocalLB.VirtualServer.create(**kwargs)
    """
    try:
        b.LocalLB.VirtualServer.create(
            definitions=[
                {
                    "name": [virtual_name],
                    "address": [address],
                    "port": [source_port],
                    "protocol": "PROTOCOL_TCP",
                }
            ],
            wildmasks=["255.255.255.255"],
            resources=[
                {"type": "RESOURCE_TYPE_POOL", "default_pool_name": [pool_name]}
            ],
            profiles=[
                [{"profile_context": "PROFILE_CONTEXT_TYPE_ALL", "profile_name": "tcp"}]
            ],
        )

        b.LocalLB.VirtualServer.set_source_address_translation_automap([virtual_name])

        set_progress("Successfully created virtual server '{}'".format(virtual_name))
    except Exception:
        set_progress("Error in creating virtual server")
        raise


def construct_load_balancer(**kwargs):
    # get the haproxy server from resource
    resource = kwargs.get("resource")

    # get common construct attributes
    members = kwargs.get("members", [])
    virtualname = kwargs.get("virtual_name", None)
    if virtual_server_name_template:
        virtualname = virtual_server_name_template
    ports = kwargs.get("ports", {})
    lbsi = kwargs.get("lbsi", None)
    f5_appliance = LoadBalancerAppliance.objects.get(id=f5_appliance_id)

    set_progress("Creating F5 load balancer object")
    # This can be replaced with an action input for static IP support
    address = F5LoadBalancer.get_address_from_resource_pool(
        kwargs.get("job"), resource, f5_appliance
    )

    f5_lb = F5LoadBalancer.objects.create(
        connection_info=f5_appliance.connection_info,
        name=virtualname,
        dns_name=address,
        resource=resource,
        service_item=lbsi,
        identifier=virtualname,
        source_port=ports["src_port"],
        destination_port=ports["dest_port"],
    )

    big = f5_lb.get_bigsuds_connection()
    f5_lb.pool_identifier = "/Common/{}".format(virtualname)
    lb_method = LB_METHOD
    create_pool(big, f5_lb.pool_identifier, lb_method, f5_lb.destination_port)
    create_virtual_server(
        big, virtualname, address, f5_lb.source_port, f5_lb.pool_identifier
    )

    f5_lb.save()

    f5_lb.add_servers(members)

    return f5_lb
