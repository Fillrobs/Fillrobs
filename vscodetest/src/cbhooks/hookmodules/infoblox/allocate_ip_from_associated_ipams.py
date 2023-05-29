"""
LEGACY: With the 9.0 release, IPAM orchestration is now provided directly on the IPAM detail page
and can be enabled and customized there.
"""


from __future__ import print_function


def run(job, logger=None):
    debug("Running hook '{}'. job.id='{}'".format(__name__, job.id), logger)
    for server in job.server_set.all():
        for custom_field_value in server.custom_field_values.filter(
            field__name__startswith="sc_nic_"
        ).exclude(field__name__endswith="_ip"):
            cb_net = custom_field_value.value.cast()
            dns_domain = cb_net.dns_domain
            if dns_domain is None:
                # fall back to the network domain
                dns_domain = server.dns_domain
            fqdn = "{}.{}".format(server.hostname, dns_domain)
            msg = ("Adding domain to hostname: {} -> {}").format(server.hostname, fqdn)
            job.set_progress(msg)

            server.host_fqdn = fqdn

            # iterate through all the associated IPAM network
            # objects until one gives an IP
            for ipam_network in cb_net.ipam_networks.all():
                try:
                    ip = ipam_network.allocate_ip_for_fqdn(fqdn)
                    if ip is not None:
                        job.set_progress(
                            "received IP {} from IPAM, setting it as static IP on Server".format(
                                ip
                            )
                        )
                        # setting server.sc_nic_0_ip, server_sc_nic_1_ip, etc
                        setattr(
                            server, "{}_ip".format(custom_field_value.field.name), ip
                        )
                        server.save()
                        break
                except Exception as e:
                    debug(
                        "caught exception trying to allocate ip for server.{}_ip: {}".format(
                            custom_field_value.field.name, e
                        ),
                        logger,
                    )
                    debug(
                        "leaving server.{}_ip unconfigured and continuing".format(
                            custom_field_value.field.name
                        ),
                        logger,
                    )


def debug(message, logger):
    if logger:
        logger.debug(message)
    else:
        print(message)
