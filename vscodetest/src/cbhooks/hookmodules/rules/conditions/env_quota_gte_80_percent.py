from __future__ import division
from past.utils import old_div
from decimal import Decimal
from infrastructure.models import Environment


THRESHOLD = Decimal("0.8")


def check(self, job, logger):
    violators = []
    environments = Environment.objects.all()
    for environment in environments:
        quotas = environment.quota_set.quotas
        for quota in quotas:
            usage = old_div(quotas[quota].used, quotas[quota].limit)
            if usage >= THRESHOLD:
                violators.add((environment.name, quota, usage))

    if len(violators) > 0:
        return (
            "",
            "",
            "",
            {"type": "Environment", "threshold": THRESHOLD, "violators": violators},
        )

    return ("", "", "", None)
