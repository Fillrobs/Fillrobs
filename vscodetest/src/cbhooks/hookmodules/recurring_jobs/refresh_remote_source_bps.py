"""
Refreshes Blueprints from Remote Source using the Remote Source URL set on each, if there is
one. Most of the actual refresh logic is performed by the refresh_from_remote_source method on
the Blueprint.
"""
import reversion

from django.conf import settings
from django.template.defaultfilters import date
from django.utils.translation import ugettext as _, ungettext

from utilities.exceptions import CloudBoltException
from common.methods import set_progress
from servicecatalog.models import ServiceBlueprint

# Combine the date and time parts so we can make a single call to the date filter
DATETIME_FORMAT = "{} {}".format(settings.SHORT_DATE_FORMAT, settings.SHORT_TIME_FORMAT)


def run(job, logger=None):
    failed_bps = []

    bps_to_refresh = ServiceBlueprint.objects.exclude(remote_source_url="").filter(
        status="ACTIVE"
    )
    num_bps_to_refresh = bps_to_refresh.count()
    if bps_to_refresh:
        set_progress(
            ungettext(
                "Found {bp_count} Blueprint with a Remote Source URL to refresh.",
                "Found {bp_count} Blueprints with a Remote Source URL to refresh.",
                num_bps_to_refresh,
            ).format(bp_count=num_bps_to_refresh)
        )
    else:
        set_progress(
            _("No Blueprints found with a Remote Source URL; nothing to refresh.")
        )
        return "SUCCESS", "", ""

    for bp in bps_to_refresh:
        set_progress(
            _('\nRefreshing Blueprint "{blueprint}" from its Remote Source URL').format(
                blueprint=bp
            )
        )
        try:
            # Reversion is used to 1. create a history event on the BP, and
            # 2. ensure that the BP reverts to its cached version if the refresh fails
            with reversion.create_revision():
                status, failure_msg = bp.refresh_from_remote_source()
                if status == "success":
                    reversion.set_comment(
                        _("Refreshed based on Remote Source URL, from Recurring Job")
                    )
                else:
                    failed_bps.append(bp)
                    # Raise an Exception because reversion requires that so it knows to revert
                    # to the previous state of the BP and properly exit the context manager
                    raise CloudBoltException(
                        _(
                            "Refresh attempt failed. Will continue to use local version "
                            "that was last refreshed {time}. Issue: {issue}"
                        ).format(
                            time=date(bp.last_cached, DATETIME_FORMAT),
                            issue=failure_msg,
                        )
                    )
        except CloudBoltException as err:
            # Just put the exception message in the progress, to continue through other BPs
            set_progress(str(err))

    set_progress(
        _("Refreshed {num_successful} of {total} Blueprints.").format(
            num_successful=num_bps_to_refresh - len(failed_bps),
            total=num_bps_to_refresh,
        )
    )

    if failed_bps:
        msg = ungettext(
            'Unable to refresh Blueprint "{blueprints}". See log for details.',
            'Unable to refresh Blueprints "{blueprints}". See log for details.',
            len(failed_bps),
        ).format(blueprints=", ".join([bp.name for bp in failed_bps]))
        return "FAILURE", msg, ""

    return "SUCCESS", "", ""
