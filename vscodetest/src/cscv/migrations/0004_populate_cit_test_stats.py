# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime
from collections import defaultdict

from django.db import migrations


def is_active(job):
    return job.status in ["PENDING", "RUNNING", "QUEUED", "TO_CANCEL"]


def get_duration(job, in_seconds=False):
    """
    From Job model.

    Return string duration in "hh:mm:ss" format if job is running or has
    completed. Returns empty string if job has not started.

    If `in_seconds` is True, returns integer.
    """
    if job.status in ['PENDING', 'QUEUED'] or not job.start_date:
        return 0 if in_seconds else ''

    # if the job is still active, or if it is in the short period of time
    # between when it is marked complete and the end_date has been saved to
    # the DB, use the current time as the end time
    if is_active(job) or not job.end_date:
        delta = datetime.datetime.now() - job.start_date
    else:
        delta = job.end_date - job.start_date

    # remove the microseconds component
    delta = delta - datetime.timedelta(microseconds=delta.microseconds)

    return delta.seconds if in_seconds else str(delta)


def get_test_job_ids_by_test_id(tests, Job):
    """
    Copied from cscv.views.cit_test_list_json, but modified because the `cit_tests` custom manager
    is not available (just had to add a filter by type).

    Returns list of IDs.
    """
    # First gather all job IDs by test ID.  Doing this single join query across 3 or 4
    # relationships now for all tests is much better than doing it per-test.
    test_jobs_by_test_id = defaultdict(list)
    test_ids = [test.id for test in tests]
    cit_test_jobs = Job.objects.\
        filter(job_parameters__functionaltestparameters__cittests__in=test_ids).\
        filter(type='functionaltest').\
        values_list('id', 'job_parameters__functionaltestparameters__cittests')
    for job_id, test_id in cit_test_jobs:
        if test_id is not None:
            test_jobs_by_test_id[test_id].append(job_id)

    return test_jobs_by_test_id


def populate_cit_test_stats(apps, schema_editor):
    """
    For all CITTests, populate new stats fields:
        last_job_passed (FK)
        last_job_failed (FK)
        last_status (str)
        last_duration (str)

    This requires doing the expensive/slow queries that the CIT list page used to do.
    """
    CITTest = apps.get_model('cscv', 'CITTest')
    Job = apps.get_model('jobs', 'Job')

    tests = CITTest.objects.all()
    test_jobs_by_test_id = get_test_job_ids_by_test_id(tests, Job)

    for test in tests:
        jobs = Job.objects.filter(id__in=test_jobs_by_test_id[test.id])

        last_job = jobs.last()
        if last_job:
            test.last_status = last_job.status
            test.last_duration = get_duration(last_job)

        test.last_job_passed = jobs.filter(status='SUCCESS').last()
        test.last_job_failed = jobs.filter(status='FAILURE').last()
        test.save()


class Migration(migrations.Migration):

    dependencies = [
        ('cscv', '0003_add_cit_test_stats_fields'),
    ]

    operations = [
        migrations.RunPython(populate_cit_test_stats)
    ]
