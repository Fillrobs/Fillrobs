"""
This plug-in can be included in a blueprint to deploy a new VM on VMware from a .ova file that
is accessible from a URL.

CloudBolt will create a Server record for this new VM so that it can be managed after the fact.
After the VM is deployed, CloudBolt will locate the new VM in VMware and update the CB server
record based on the details of the VM.

Prerequisites:
 * ovftool needs to be installed on a server that is under CB management (this can be the CB
 server itself)
 * CB 8.3-alpha5 or newer
"""
import re

from common.methods import set_progress, uniquify_hostname_with_padding
from infrastructure.models import Environment, Server, CustomField
from orders.views import get_optional_values_for_field
from utilities.models import GlobalPreferences
from utilities import events


def generate_options_for_env_id(**kwargs):
    envs = Environment.objects.filter(
        resource_handler__resource_technology__name="VMware vCenter"
    ).values("id", "name")
    options = [(env["id"], env["name"]) for env in envs]
    return options


def generate_options_for_network_name(control_value=None, **kwargs):
    if not control_value:
        return []
    env = Environment.objects.get(id=control_value)
    nic_1_cf = CustomField.objects.get(name="sc_nic_0")
    possible_option_info = get_optional_values_for_field(
        nic_1_cf, environment=env, group=None, constrained=True
    )
    possible_options = [
        net_cfv.value.network for net_cfv in possible_option_info.get("options")
    ]
    return possible_options


def generate_options_for_datastore(control_value=None, **kwargs):
    if not control_value:
        return []
    env = Environment.objects.get(id=control_value)
    datastore_cf = CustomField.objects.get(name="vmware_datastore")
    possible_option_info = get_optional_values_for_field(
        datastore_cf, environment=env, group=None, constrained=True
    )
    cfv_options = possible_option_info.get("options")
    set_progress(f"generate_options_for_datastore cfv_options = {cfv_options}")
    possible_options = [cfv.value for cfv in cfv_options]
    print(possible_options)
    return possible_options


def determine_hostname(hostname):
    """
    Expand the 00X part of the hostname, if it has one.

    Eventually, this could also check for a hostname template on the env, globally, etc.
    """
    case_sensitive = GlobalPreferences.get_preference(
        "hostname_case_sensitivity", False
    )
    mo = re.search("(0+X)", hostname)
    if mo:
        match = mo.groups()[0]
        hostname = uniquify_hostname_with_padding(
            hostname, match, bad_hostnames=[], case_sensitive=case_sensitive
        )
    return hostname


def create_server_record(job, rh, env, vmname):
    """
    Create and save a new Server record in "Provisioning" state.

    :return: the Server object.
    """
    # the parent job is the deploy BP job that has an order associated with it
    group = job.parent_job.get_order().group
    server = Server(
        hostname=vmname,
        group=group,
        owner=job.owner,
        environment=env,
        resource_handler=rh,
        status="PROV",
        power_status="POWEROFF",
    )
    server.save()
    job.server_set.add(server)
    msg = "Server created by OVA deployment job"
    events.add_server_event("CREATION", server, msg, profile=job.owner, job=job)
    return server


def refresh_info(server):
    """
    Find the UUID for the VM in VMware based on its name, update the Server record to ACTIVE and
    save its latest info.

    :return: the updated Server record
    """
    vm = server.resource_handler.get_vm_dict(server)
    server.resource_handler_svr_id = vm["uuid"]
    server.status = "ACTIVE"
    server.refresh_info()
    return server


def run(job, *args, **kwargs):
    ova_url = "{{ ova_url }}"
    env = int("{{ env_id }}")
    env = Environment.objects.get(id=env)
    network_name = "{{ network_name }}"
    datastore = "{{ datastore }}"
    hostname = "{{ hostname }}"

    rh = env.resource_handler.cast()
    username = rh.serviceaccount
    passwd = rh.servicepasswd
    ip = rh.ip
    hostname = determine_hostname(hostname)
    server = create_server_record(job, rh, env, hostname)

    cluster_path = rh.get_path_to_cluster(env.vmware_cluster)
    ovftool_cmd = (
        f"ovftool --allowExtraConfig -ds={datastore} --X:logToConsole --X:logLevel=info --network='{network_name}' "
        f"--X:defaultSslCiphers -n='{hostname}' "
        f"{ova_url} 'vi://{username}:{passwd}@{ip}/{cluster_path}'"
    )

    # Running this via execute_command() or run_command() causes ovftool to bomb out w/o an error
    # right after the "Enable SSL verification" log message. We believe that is because celery is
    # altering the environment in some way (perhaps monkey-patching HttpConnectionPool).
    # 2018-08-08T18:29:22.478-04:00 verbose OVFTool[16300] [Originator@6876 sub=Default] Constructing URL...
    # 2018-08-08T18:29:22.478-04:00 verbose OVFTool[16300] [Originator@6876 sub=Default] Connecting to vi host 10.60.100.10
    # 2018-08-08T18:29:22.478-04:00 verbose OVFTool[16300] [Originator@6876 sub=Default] Enable SSL verification
    # 2018-08-08T18:29:22.478-04:00 verbose OVFTool[16300] [Originator@6876 sub=HttpConnectionPool-000000] HttpConnectionPoolImpl created. maxPoolConnections = 20; idleTimeout = 900000000; maxOpenConnections = 20; maxConnectionAge = 0
    # stdout = execute_command(
    #     ovftool_cmd,
    #     timeout=3600,
    #     strip=[passwd],
    #     stream_title="Deploying OVA")

    # As a workaround, find the CB server and run as a remote script on that.
    ovftool_server = Server.objects.get(id="{{ ovftool_server_id }}")
    stdout = ovftool_server.execute_script(script_contents=ovftool_cmd)
    refresh_info(server)
    server.power_on(profile=job.owner)

    # This is intentionally left commented out. It depends on VMware tools being installed,
    # which is not usually the case for VMs just deployed from OVAs, but it could be uncommented
    # for situations where VMware tools is included in the OVA.
    # server.wait_for_os_readiness()

    return "SUCCESS", stdout, ""
