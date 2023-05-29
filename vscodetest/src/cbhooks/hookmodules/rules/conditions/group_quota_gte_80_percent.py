from __future__ import division
from past.utils import old_div
from decimal import Decimal
from accounts.models import Group


THRESHOLD = Decimal("0.8")


def check(job, logger):
    violators = []
    groups = Group.objects.all()
    for group in groups:
        job.set_progress("Examining group {}".format(group.name))
        quotas = group.quota_set.quotas
        violator = {"group": group.id}
        violator_quotas = []
        for quota in quotas:
            quotax = quotas[quota]
            usage = old_div(quotax.used, quotax.limit)
            if usage >= THRESHOLD:
                job.set_progress(
                    ("Quota {} exceeds threshold: used={}, limit={}").format(
                        quota, quotax.used, quotax.limit
                    )
                )
                violator_quotas.append(
                    {"quota_id": quotax.id, "quota_name": quota, "usage": usage}
                )
        if len(violator_quotas) > 0:
            job.set_progress(
                ("Including Group {} because of {} exceeded quota(s).").format(
                    group.name, len(violator_quotas)
                )
            )
            violator["quotas"] = violator_quotas
            violators.append(violator)

    if len(violators) > 0:
        job.set_progress(
            ("Found quotas that exceed threshold {:.0%}.").format(THRESHOLD)
        )
        return (
            "",
            "",
            "",
            {"type": "Group", "threshold": THRESHOLD, "violators": violators},
        )

    return ("", "", "", None)
