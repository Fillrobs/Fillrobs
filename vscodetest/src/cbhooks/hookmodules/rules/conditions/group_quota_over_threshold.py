from __future__ import division
from past.utils import old_div
from decimal import Decimal
from accounts.models import Group


THRESHOLD = Decimal("{{ threshold }}")


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
            if quotax.limit == 0:
                if quotax.used == 0:
                    usage = 0
                else:
                    usage = 1
            else:
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
            ("Found quotas that exceed threshold {}%.").format(THRESHOLD * 100)
        )
        return (
            "SUCCESS",
            "",
            "",
            {"type": "Group", "threshold": THRESHOLD, "violators": violators},
        )

    return ("SUCCESS", "", "", None)
