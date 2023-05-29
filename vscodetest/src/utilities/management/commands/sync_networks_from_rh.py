#!/usr/local/bin/python
from __future__ import unicode_literals

"""
django-admin command for importing networks from a resource handler into the CB
database. Currently only works for VMware resource handlers.

For example:
    ./manage.py sync_networks_from_rh
"""
from future import standard_library

standard_library.install_aliases()

# @THIS IS MAGIC
# @Preemptively import the standard 'commands' module, to avoid package name
# @conflicts with this module (also named 'commands') when using
# @utility.run_commands() from resource handler.  Not fully understood. @@@
import sys
import logging
from collections import defaultdict

from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType

from resourcehandlers.models import ResourceHandler, ResourceNetwork
from resourcehandlers.vmware.models import VsphereResourceHandler

logger = logging.getLogger("sync_networks_from_rh")

SUPPORTED_RH_TYPES = [VsphereResourceHandler]
SUPPORTED_RH_TYPES = [
    ContentType.objects.get_for_model(rht) for rht in SUPPORTED_RH_TYPES
]


def configure_logging(filename):
    """
    Configure the logger such that all run-time output, either emitted directly
    from this script or indirectly via the CloudBolt machinery, is captured
    *here* and does not pollute the application logs.
    """
    if filename:
        # Direct all output to the specified file
        handler = logging.handlers.RotatingFileHandler(
            filename, mode="a", maxBytes=1024 * 1024, backupCount=3
        )
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        )
        level = logging.DEBUG  # Capture debug output during the cron job

    else:
        # Direct all output to the console
        handler = logging.StreamHandler(stream=sys.stdout)
        formatter = logging.Formatter("%(message)s")
        level = logging.INFO  # Minimize debug output on the console

    handler.setLevel(level)
    handler.setFormatter(formatter)

    # Configure the top-level (root) logger with these settings
    logger.handlers = []  # @@disable handlers inherited from settings.py
    logger.setLevel(level)

    # FIXME for some reason adding this handler will print log messages twice,
    # so for now just adding it when a specific log file is requested:
    # @@some kind of interaction between manage.py and settings.LOGGING{}
    if filename:
        logger.addHandler(handler)

    return


def find_network_obj(net_info):
    """
    Return a list of networks in CloudBolt that match the given info.
    """

    # NOTE: We are looking for all matching networks (not just those in this
    # RH) on purpose. This way RH.add_network() will work correctly.
    # Fix for https://cloudbolt.atlassian.net/browse/DEV-847

    nets = []
    for net in ResourceNetwork.objects.all():
        net = net.cast()
        if net.network == net_info["network"]:
            nets.append(net)

    return nets


def import_networks(rh, create=True):
    """
    Create, save, and return records for each network that we can find by
    querying the resource handler. Does not overwrite existing network records.
    Returns a list of networks that need to be attached to the RH.
    """
    logger.info("Scanning resource handler '%s'..." % (rh.name))
    networks_info = rh.get_all_networks()
    logger.info("Found %s networks in %s:" % (len(networks_info), rh.name))

    # used to left-justify the network names for prettier output
    max_name_width = max([len(info["network"]) for info in networks_info])

    # list of networks that should be attached to all RHs that share this IP address
    networks_to_attach = []
    new_count = 0

    for net_info in networks_info:
        just_net_name = (net_info["network"] + ":").ljust(max_name_width + 1)
        if net_info["network"].find("plink") > 0:
            logger.info(
                "  %s skipping because it is a dvPortGroup uplink "
                "network" % (just_net_name)
            )
            continue

        if not create:
            logger.info(
                "  %s not creating because create mode is disabled" % (just_net_name)
            )
            continue

        cb_nets = find_network_obj(net_info)
        if cb_nets:
            if len(cb_nets) > 1:
                ids_str = ", ".join((str(net.id) for net in cb_nets))
                logger.warning(
                    "  %s more than one correspoding networks found in CloudBolt (%s); skipping..."
                    % (just_net_name, ids_str)
                )
            else:
                cb_net = cb_nets[0]
                logger.info(
                    "  %s pre-existing record was found (id=%s)"
                    % (just_net_name, cb_net.id)
                )
                networks_to_attach.append(cb_net)

                # Distributed virtual portgroups can be renamed, but supposedly keep the
                # same key (UUID):
                if net_info["network"] != cb_net.network:
                    logger.info(
                        "  Updating name of network from %s to %s"
                        % (cb_net.network, net_info["network"])
                    )
                    cb_net.network = net_info["network"]
                    cb_net.save()
        else:
            # This network does not have an entry in CloudBolt
            # Will find this network in CB (or create it if it does not exist),
            # and will attach it to this RH:
            # NOTE: later on we will attach this network to all RHs that
            # have the same IP as this RH; that's why we add the network to the
            # "networks_to_attach" list.
            cb_net, created = rh.add_network(**net_info, tenant=rh.tenant)
            if not created:
                # Should never happen
                raise RuntimeError(
                    "Adding network to RH '%s' showed that network already exists" % rh
                )

            # Remove this new network from the list of RHs networks, so that we
            # can add it (with logging) later in the workflow:
            # FIXME This is a bit hacky, and deserves refactoring in the future.
            rh.networks.remove(cb_net)
            networks_to_attach.append(cb_net)

            new_count += 1
            logger.info("  %s creating a new record" % just_net_name)

    logger.info("Created %s new network records." % (new_count))

    return networks_to_attach


def uniquify_rhs(old_rhs):
    """
    Eliminate RHs that have the same IP address as RHs earlier in the list.
    This is so we don't scan the same RH multiple times.
    """
    new_rhs = []
    ips_seen = []
    for old_rh in old_rhs:
        if old_rh.ip not in ips_seen:
            ips_seen.append(old_rh.ip)
            new_rhs.append(old_rh)
    return new_rhs


def find_rhs(rh_name):
    """
    Return a list of ResourceHandler objects filtered by name.
    Returns all ResourceHandlers if `rh_name` is 'all', otherwise returns the
    one ResourceHandler with name matching `rh_name`.
    """
    if rh_name == "all":
        rhs = ResourceHandler.objects.filter(real_type__in=SUPPORTED_RH_TYPES)
    else:
        rhs = [ResourceHandler.objects.get(name=rh_name)]

    rhs = [rh.cast() for rh in rhs]

    return uniquify_rhs(rhs)


def main(rh_name, create):
    """
    Main function that does all there work import importing networks.

    create - Whether to create new network objects in CloudBolt (default True)
    """
    rhs = find_rhs(rh_name)

    logger.info("Found %s distinct resource handlers to scan." % len(rhs))

    rhIP_to_rhs = defaultdict(list)
    for rh in rhs:
        rhIP_to_rhs[rh.ip].append(rh)

    for rh_ip, rhs in list(rhIP_to_rhs.items()):
        # <rhs> is a list of all RHs that share the ip of the rh we just imported networks from

        unique_rh = rhs[0]
        rh_networks = import_networks(unique_rh, create)

        for rh in rhs:
            networks_to_attach = [
                net for net in rh_networks if net not in rh.networks.all()
            ]
            if networks_to_attach:
                logger.info(
                    "Attaching these networks to RH '%s':\n  %s"
                    % (rh, "\n  ".join([n.network for n in networks_to_attach]))
                )
                rh.networks.add(*networks_to_attach)
        logger.info("Done attaching.")


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "-r",
            "--resource-handler",
            help='Resource handler.  Specifying "all" will use all RHs',
            default="all",
        )
        parser.add_argument(
            "--no-create",
            help="Do not create new network objects",
            action="store_true",
            default=False,
        )
        parser.add_argument(
            "--logfile",
            help="Location of the output log file for this operation (optional).",
        )

    def handle(self, *args, **options):
        configure_logging(options["logfile"])

        create = not options["no_create"]
        rh = options["resource_handler"]
        main(rh, create)
