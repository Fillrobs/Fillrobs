#!/usr/local/bin/python
from __future__ import unicode_literals

"""
django-admin command for running CloudBolt CIT job.

Usage:
    ./manage.py run_cit -h

"""
import sys
import time

from django.core.management.base import BaseCommand

import os
from cscv.models import CITTest
from jobs.models import Job, FunctionalTestParameters
from utilities.exceptions import TimeoutException
from utilities.logger import ThreadLogger
from utilities.models import GlobalPreferences

os.environ["DJANGO_SETTINGS_MODULE"] = "settings"

logger = ThreadLogger(__name__)


class Command(BaseCommand):
    help = "Runs the Continuous Infrastructure Testing (CIT) job."

    def add_arguments(self, parser):
        parser.add_argument(
            "-w",
            "--wait",
            action="store_true",
            help="Wait for CIT job to complete before exitingd",
        )
        parser.add_argument(
            "-t", "--timeout", help="Timeout in seconds to wait for job to complete"
        )
        parser.add_argument(
            "-l",
            "--labels",
            metavar="LABELS",
            help="Run tests labelled with any label in LABELS (comma separated)",
        )

    def handle(self, *args, **options):
        wait = options.get("wait")
        timeout = options.get("timeout")
        if wait and not timeout:
            logger.warning("Timeout argument required if wishing to wait")
            sys.exit(1)

        if not CITTest.objects.filter(enabled=True).exists():
            logger.info("No enabled CIT Tests to run.")
            sys.exit(0)

        job_params = FunctionalTestParameters.objects.create()
        # Currently supports either filtering on labels or running all CIT tests
        if options["labels"]:
            label_list = options["labels"].split(",")
            job_params.labels_to_run.set(*label_list)
        else:
            job_params.run_full_suite = True
        job_params.failure_email_address = GlobalPreferences.get().cbadmin_email
        job_params.save()

        job = Job(job_parameters=job_params, type="functionaltest")
        job.save()
        logfile = job.get_log_file_path()

        logger.info("Created job: {}".format(job))
        logger.info("Job log file: {}".format(logfile))

        status = "SUCCESS"
        if wait:
            status = wait_for_job_completion(job, timeout=timeout)

        logger.info("Exiting")
        # Anything that is not a "SUCCESS" should be considered a failure (exit 1)
        sys.exit(0 if status == "SUCCESS" else 1)


def wait_for_job_completion(job, timeout=120):
    """
    Wait for the given job to complete, raise TimeoutException if timeout
    reached. Return boolean of if the job ended in success or not.
    """
    start_time = time.time()
    timeout_time = start_time + int(timeout)
    last_prog_msg_id = 0

    while time.time() < timeout_time:
        job = Job.objects.get(id=job.id)

        prog_msgs = job.progressmessage_set.filter(id__gt=last_prog_msg_id)
        for prog_msg in prog_msgs.order_by("id").iterator():
            logger.info(prog_msg.message)
            last_prog_msg_id = prog_msg.id

        if not job.is_active():
            logger.info(
                "Job completed with status: {}, output: {}, errors: {}".format(
                    job.status, job.output, job.errors
                )
            )
            return job.status
        time.sleep(60)

    else:
        raise TimeoutException("Timeout waiting for job to complete")
