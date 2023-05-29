#!/usr/bin/env python

"""
This action should be run as a recurring job,
"""

import datetime
import os
import sys

from django.db.models import Q

os.environ["DJANGO_SETTINGS_MODULE"] = "settings"
sys.path.append("/opt/cloudbolt")
from utilities.logger import ThreadLogger

logger = ThreadLogger(__name__)
from jobs.models import Job
from common.methods import set_progress
from django.conf import settings


def run(job, *args, **kwargs):
    threshold_days = "{{ threshold_days }}"
    sync_job_threshold_days = "{{ sync_job_threshold_days }}"
    if not threshold_days:
        threshold_days = 365
    if not sync_job_threshold_days:
        sync_job_threshold_days = 7

    delete_date = datetime.datetime.now() - datetime.timedelta(days=int(threshold_days))
    sync_delete_date = datetime.datetime.now() - datetime.timedelta(
        days=int(sync_job_threshold_days)
    )
    msg = "Will delete sync jobs older than {} days (from before {}) ".format(
        sync_job_threshold_days, sync_delete_date.date()
    )
    msg += "and other jobs older than {} days (from before {})".format(
        threshold_days, delete_date.date()
    )
    set_progress(msg)

    normal_job_query = Q(start_date__lt=delete_date)
    sync_job_query = Q(type="syncvms") & Q(start_date__lt=sync_delete_date)
    old_jobs = Job.objects.filter(normal_job_query | sync_job_query)

    # Excluding RUNNING jobs will prevent this from from deleting its own job record, as well as
    # any that are PENDING, QUEUED, in the process of being canceled, etc
    old_jobs = old_jobs.exclude(status__in=Job.ACTIVE_STATUSES)
    old_job_ids = old_jobs.values_list("id", flat=True)

    set_progress("Found {} jobs to delete".format(len(old_job_ids)))
    for job_id in old_job_ids:
        logfile = os.path.join(
            settings.VARDIR,
            "log",
            "cloudbolt",
            "jobs",
            "{}{}".format(str(job_id), ".log"),
        )
        if os.path.exists(logfile):
            os.remove(logfile)
    old_jobs.delete()
    return ("SUCCESS", "", "")


if __name__ == "__main__":
    run()
