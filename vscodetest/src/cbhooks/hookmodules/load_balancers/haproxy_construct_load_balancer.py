from common.methods import set_progress
from networks.models import HAProxy

# HA Proxy specific inputs
haproxy_tier = "{{ haproxy_tier }}"
install_haproxy = "{{ install_haproxy }}"


def construct_load_balancer(**kwargs):
    # get the haproxy server from resource
    resource = kwargs.get("resource")
    hap_server = resource.server_set.filter(service_item__id=int(haproxy_tier)).first()

    # get common construct attributes
    members = kwargs.get("members", [])
    virtualname = kwargs.get("virtual_name", None)
    ports = kwargs.get("ports", {})
    lbsi = kwargs.get("lbsi", None)

    if install_haproxy == "True":
        cmd = """
yum -y install haproxy
sed -i \"/127.0.0.1:500/d\" /etc/haproxy/haproxy.cfg
sed -i \"s/frontend  main \*:5000/frontend  main \*:{}/\" /etc/haproxy/haproxy.cfg
chkconfig --level 35 haproxy on
service haproxy start
        """.format(  # noqa: W605
            ports["src_port"]
        )
        set_progress("Installing haproxy with command:\n{}".format(cmd))
        hap_server.execute_script(script_contents=cmd, timeout=600, run_with_sudo=True)

    hap_lb = HAProxy.objects.create(
        server=hap_server,
        name=virtualname,
        dns_name=hap_server.ip,
        resource=resource,
        service_item=lbsi,
        identifier=virtualname,
        source_port=ports["src_port"],
        destination_port=ports["dest_port"],
    )

    hap_lb.add_servers(members)

    return hap_lb


def generate_options_for_haproxy_tier(blueprint=None, **kwargs):
    """
    Returns a list of PSSI choices, which are used as options for acting on a
    specific tier of the resource when it gets deployed.
    """
    if not blueprint:
        return []
    options = [(pssi.id, pssi.name) for pssi in blueprint.pssis()]
    return options
