from common.methods import set_progress


def remove_members_from_load_balancer(**kwargs):

    # get common construct attributes
    lb = kwargs.get("lb")
    members = kwargs.get("members", [])

    hap_server = lb.server

    cmd_tpl = 'sed -i "/{0}/d" /etc/haproxy/haproxy.cfg'
    for m in members:
        cmd = cmd_tpl.format(m.ip)
        set_progress("Removing server member with command:\n{}".format(cmd))
        hap_server.execute_script(script_contents=cmd, run_with_sudo=True)

    set_progress("Restarting haproxy service")

    hap_server.execute_script(
        script_contents="service haproxy restart", run_with_sudo=True
    )
