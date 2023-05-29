"""
Connect Networks associated with a Resource Handler (`ResourceNetwork`) with
an IPAM CIDR.

Note: The plugin has been replaced with a page in the UI. Please visit
"https://YOUR.CLOUDBOLT.URL/ipam/"
"""

from ipam.models import IPAMNetwork
from resourcehandlers.models import ResourceNetwork


# Note: Networks can only be associated with a single IPAM CIDR.
MAPPING = {
    "ENG-VLAN060 Long-Term": "10.50.31.0/24",
    "ENG-VLAN064 Short-Term": "192.168.3.0/24",
}


def run(job, logger=None):
    for cloudbolt_network_name, ipam_network_cidr in MAPPING.items():
        cb_net = ResourceNetwork.objects.filter(name=cloudbolt_network_name).first()
        ipam_net = IPAMNetwork.objects.filter(CIDR=ipam_network_cidr).first()

        if cb_net is not None and ipam_net is not None:
            cb_net.ipam_network = ipam_net
            cb_net.save()

        else:
            logger.info(
                "Could not associate {} with {}. Make sure a Network exists "
                "with that name and that the CIDR is associated with an IPAM "
                "Network.".format(cloudbolt_network_name, ipam_network_cidr)
            )

    return
