"""
Provided in this module are the 4 signature methods that define interactions with phpIPAM.
"""


def is_hostname_valid(phpipam, server, network):
    """
    Code defined here will be executed at the Pre-Create Resource trigger point.
    """
    wrapper = phpipam.get_api_wrapper()
    host = wrapper.get_host_on_network(
        server.hostname, network.ipam_network.cast().phpipam_id
    )
    return host is None


def allocate_ip(phpipam, server, network):
    """
    Code defined here will be executed at the Pre-Create Resource trigger point.
    """
    wrapper = phpipam.get_api_wrapper()
    ip = wrapper.add_host_record_for(
        network.ipam_network.cast().phpipam_id, server.hostname
    )

    return ip


def delete_host(phpipam, host_fqdn, network):
    """
    Code defined here will be executed at the Post-Decomission trigger point.
    """
    wrapper = phpipam.get_api_wrapper()
    wrapper.delete_host_record(host_fqdn, network.ipam_network.cast().phpipam_id)


def delete_host_by_nic(phpipam, hostname, network):
    """
    Code defined here will be executed when NICs are removed individually.
    Implemented as an additional method to avoid complications with other IPAM solutions that don't support this yet.
    """
    wrapper = phpipam.get_api_wrapper()
    wrapper.delete_host_record(hostname, network.ipam_network.cast().phpipam_id)
