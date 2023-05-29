#!/bin/env python
import time  # noqa: F841, F401

from connectors.puppet_ent.puppet_ent_api import PECertificateEndpoint
from infrastructure.models import Server


def run(logger=None, **kwargs):
    """
    This is the delete_server_from_connector action that is used by Puppet
    Enterprise 3.X to remove a node during decommissioning.
    """
    peconf = kwargs.get("peconf", None)
    if not peconf:
        return (
            "FAILURE",
            "Can't run this action without a puppet enterprise configuration!",
            "",
        )

    server = kwargs.get("server")
    assert isinstance(server, Server)

    # Get Cert Name
    logger.info("Getting cert name")
    pen = server.pe_node
    cert_name = pen.certname
    if not cert_name:
        return "FAILURE", "Cannot obtain cert name so cannot delete server from PE", ""

    # Unpin server from groups. Must call remove_node_from_all_groups feature from here because
    # the feature is 3.X version only. When version support is added this can be reconsidered
    peconf.remove_node_from_all_groups(server)

    # Clean certificate on PE master
    peconf.clean_cert(cert_name)

    # Remove the node's cert from PE
    logger.info("Removing cert from PE")
    api = PECertificateEndpoint(peconf)
    api.delete_cert(cert_name)

    # delete the node reference from CB db
    pen.delete()

    return "", "", ""
