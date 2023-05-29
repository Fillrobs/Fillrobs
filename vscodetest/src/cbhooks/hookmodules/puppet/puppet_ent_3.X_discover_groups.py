from connectors.puppet_ent.puppet_ent_api import PEGroupsEndpoint
from connectors.puppet_ent.models import PEGroup
from utilities.exceptions import CloudBoltException

from utilities.logger import ThreadLogger

logger = ThreadLogger(__name__)


def discover_groups(**kwargs):
    """
    This is the discover_groups action that is used by Puppet
    Enterprise 3.X to determine which groups are available in PE and make
    PEGroup objects for them. Used to import groups.
    """

    peconf = kwargs.get("peconf", None)
    if not peconf:
        raise CloudBoltException(
            "Can't run this action without a puppet enterprise configuration!"
        )

    ignored_groups = ["default", "PE.*"]
    api = PEGroupsEndpoint(peconf)
    groups = []
    group_reps = [g for g in api.get_groups().json() if g["name"] not in ignored_groups]
    for g in group_reps:
        group = PEGroup()
        group.name = g["name"]
        group.pe_conf = peconf
        group.uuid = g["id"]
        groups.append(group)
    return groups
