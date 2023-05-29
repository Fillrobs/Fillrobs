"""
Provided in this module are the 4 signature methods that define interactions with solarWindsIpam.
"""


def is_hostname_valid(solarwinds, server, network=None):
    """
    Code defined here will be executed at the Pre-Create Resource trigger point.
    """
    wrapper = solarwinds.get_api_wrapper()
    host = wrapper.get_host_by_name(server.hostname)
    return host is None


def allocate_ip(solarwinds, server, network):
    """
    Code defined here will be executed at the Pre-Create Resource trigger point.
    """
    ip = None
    wrapper = solarwinds.get_api_wrapper()
    ip = wrapper.add_host_record_for(
        network.ipam_network.cast().subnet_id, server.hostname
    )

    return ip


def delete_host(solarwinds, host_fqdn, network=None):
    """
    Code defined here will be executed at the Post-Decomission trigger point.
    """
    wrapper = solarwinds.get_api_wrapper()
    wrapper.delete_host_record(host_fqdn)
