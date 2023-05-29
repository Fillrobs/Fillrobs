"""
Syncs Resources using the Discovery Plug-in set on each Blueprint, if there is
one. Most of the actual sync logic is performed by the sync_resources method on
the Blueprint.
"""
from django.utils.translation import ugettext as _, ungettext

from common.methods import set_progress
from servicecatalog.models import ServiceBlueprint


def run(job, logger=None):
    failed_bps = []

    bps_to_sync = ServiceBlueprint.objects.filter(
        discovery_plugin__isnull=False, status="ACTIVE"
    )
    if bps_to_sync:
        set_progress(
            ungettext(
                "Found {bp_count} Blueprint with a Discovery Plug-in to sync.",
                "Found {bp_count} Blueprints with a Discovery Plug-in to sync.",
                bps_to_sync.count(),
            ).format(bp_count=bps_to_sync.count())
        )
    else:
        set_progress(
            _("No Blueprints found with a Discovery Plug-in; nothing to sync.")
        )

    for bp in bps_to_sync:
        set_progress(
            _('\nRunning sync on Blueprint "{blueprint}"').format(blueprint=bp)
        )
        succeeded = bp.sync_resources()
        if not succeeded:
            failed_bps.append(bp)

    if failed_bps:
        msg = ungettext(
            'Unable to sync Resources for Blueprint "{blueprints}". See log for details.',
            'Unable to sync Resources for Blueprints "{blueprints}". See log for details.',
            len(failed_bps),
        ).format(blueprints=", ".join([bp.name for bp in failed_bps]))
        return "FAILURE", msg, ""

    return "SUCCESS", "", ""
