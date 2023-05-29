"""
Sends group quota warnings for each group with a quota violation. The email
will be sent to all group members with the "Manage Subgroup Quotas" permission,
so ensure that your group admins have this permission before using this action.
"""
from django.utils.translation import ugettext as _

from accounts.models import Group
from quota.models import Quota
from utilities.mail import email


def run(job, logger=None):
    job.set_progress("Preparing to send group quota warning emails.")
    params = job.job_parameters.cast().arguments
    threshold = params["threshold"]
    for violator in params["violators"]:
        group_id = violator["group"]
        group = Group.objects.filter(id=group_id).first()
        quotas = []
        for quota_data in violator["quotas"]:
            quotas.append(
                {
                    "id": quota_data["quota_id"],
                    "name": quota_data["quota_name"],
                    "usage": "{}%".format(quota_data["usage"] * 100),
                    "obj": Quota.objects.filter(id=quota_data["quota_id"]).first(),
                }
            )

        group_admins = group.get_profiles_for_permission(
            "group.manage_subgroup_quotas", include_global_roles=False
        )
        recipients = [profile.user.email for profile in group_admins]
        job.set_progress("\nTO: {}".format(", ".join(recipients)))

        email_context = {"threshold": threshold, "group": group, "quotas": quotas}

        if recipients is None:
            job.set_progress(_("No recipients specified"))
            return ("FAILURE", "", "no recipients configured")

        try:
            email(
                recipients=recipients, slug="group-quota-warning", context=email_context
            )
        except Exception as e:
            return ("FAILURE", "", "error sending email: {}".format(e))

    return ("", "", "")
