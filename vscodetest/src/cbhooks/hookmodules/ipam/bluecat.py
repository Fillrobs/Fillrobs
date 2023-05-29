"""
Provided in this module are the signature methods that define interactions with BlueCat.
"""


def is_hostname_valid(bluecat, server, network=None):
    """
    Call out to BlueCat to verify that a given hostname is not already in use

    Code defined here will be executed at the Pre-Create Resource trigger point.
    """
    wrapper = bluecat.get_api_wrapper()
    host = wrapper.get_host_by_name(server.hostname)
    return host is None


def allocate_ip(bluecat, server, network):
    """
    Call out to BlueCat to allocate an IP address for a given hostname.

    Code defined here will be executed at the Pre-Create Resource trigger point.
    """
    wrapper = bluecat.get_api_wrapper()
    bluecat_network = network.ipam_network.cast()
    address = wrapper.assign_next_available_ip(
        bluecat_network.configuration_id,
        bluecat_network.bluecat_id,
        hostname=server.hostname,
        domain=network.dns_domain,
        properties=f"name={server.hostname}",
    )
    ip = address["properties"]["address"]

    return ip


def delete_host(bluecat, host_fqdn, network=None):
    """
    Call out to BlueCat to remove a host record and free up that hostname/IP.

    Code defined here will be executed at the Post-Decomission trigger point
    """
    wrapper = bluecat.get_api_wrapper()
    wrapper.delete_host_record(host_fqdn)
