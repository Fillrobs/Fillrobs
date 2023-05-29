from common.methods import set_progress


def add_members_to_load_balancer(**kwargs):

    # get common construct attributes
    lb = kwargs.get("lb")
    members = kwargs.get("members", [])

    hap_server = lb.server

    cmd_tpl = 'sed -i "/backend app/a\ \ \ \ server {0} {1}:{2} check" /etc/haproxy/haproxy.cfg'  # noqa: W605
    for m in members:
        cmd = cmd_tpl.format(m.hostname, m.ip, lb.destination_port)
        set_progress("Adding server member with command:\n{}".format(cmd))
        hap_server.execute_script(script_contents=cmd, run_with_sudo=True)

    set_progress("Restarting haproxy service")

    hap_server.execute_script(
        script_contents="service haproxy restart", run_with_sudo=True
    )
