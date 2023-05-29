from common.methods import set_progress


def run(job=None, logger=None, **kwargs):
    """
    This action is used to translate the IP addresses stored for servers and
    their NICs in CloudBolt based on provided NAT Info. It is a sample of one
    way this translation can be done, and of the kind of script that can be run
    at the Pre Server Refresh trigger point.

    The desired NAT Info should be set on the pertinent network(s) by listing
    the first 3 desired octets and using an x for the 4th. (ex: 192.168.25.x)
    For each NIC on the server, its network will be checked for such NAT Info.
    If it exists, the IP for that NIC will be translated by replacing the first
    3 octets of the IP with the 1st 3 from the NAT Info, and leaving the 4th
    octet. The overall IP of the server will be set to the translated IP for the
    first NIC (index 0).

    This process occurs during server refresh, before a comparison is made between the dictionary
    data from the RH (which is modified here) and the information stored on the server in
    CB. Original IP will be set as the private IP for each NIC.
    """
    server = kwargs.get("server")
    vm_dict = kwargs.get("vm_dict")

    for nic in server.nics.all():
        network = nic.network
        if network:
            nat_info = network.nat_info
            if nat_info:
                dict_nics = vm_dict["nics"]
                if dict_nics:
                    set_progress(
                        "Network {} of NIC {} on server {} has NAT Info {}. Translating IP.".format(
                            network, nic.index, server.hostname, nat_info
                        )
                    )
                    dict_nic = dict_nics[nic.index]
                    # Assumption: NAT info is in format 192.168.25.x

                    parsed_nat = nat_info.split(".")
                    if len(parsed_nat) != 4:
                        set_progress("NAT Info must be in format 192.168.25.x. Exiting")
                        return "FAILURE", "", "Incorrect NAT Info format"
                    parsed_ip = dict_nic["ip_address"].split(".")
                    if len(parsed_ip) != 4:
                        set_progress("IP is somehow set to incorrect format. Exiting")
                        return "FAILURE", "", "Incorrect IP format"
                    last_octet = parsed_ip[3]
                    new_ip_parts = [
                        parsed_nat[0],
                        parsed_nat[1],
                        parsed_nat[2],
                        last_octet,
                    ]
                    new_ip = new_ip_parts.join(".")
                    # preserve original IP info for this nic
                    dict_nic["private_ip"] = dict_nic["ip_address"]

                    # set NAT'ed IP as the main IP on the interface
                    dict_nic["ip_address"] = new_ip

                    # Also set the server's main IP to the new IP for NIC 0
                    if nic.index == 0:
                        vm_dict["ip"] = new_ip
    return "", "", ""
