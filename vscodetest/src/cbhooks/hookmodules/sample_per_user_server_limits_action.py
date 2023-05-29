def run(job, logger=None, **kwargs):
    """
    This is a sample pre-provision action that can be used to prevent
    provisioning when allowing it to continue would cause the number of servers
    a user owns to exceed the desired number of maximum servers per user.

    Tries to use the maximum number of servers per user from a custom field value, CFV (a.k.a. parameter) set on the
    UserProfile. The CFV could have been mapped from an LDAP utility.
    Otherwise, use the action input, which is set to 10 out of the box in CloudBolt.

    A similar approach could be used to prevent provisioning based on other
    user-specific limits, such as CPU.
    """
    svr_cnt = job.owner.server_set.count()

    max_servers = job.owner.get_value_for_custom_field("max_servers")

    if not max_servers:
        max_servers = int("{{ max_servers_per_user }}")

    if svr_cnt >= max_servers:
        return (
            "FAILURE",
            "You already own {} servers, and the maximum number of servers per user is {}".format(
                svr_cnt, max_servers
            ),
            "",
        )

    return "", "", ""
