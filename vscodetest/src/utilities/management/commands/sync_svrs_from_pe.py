#!/usr/local/bin/python
from __future__ import unicode_literals

"""
django-admin command for running CB sync servers from provision engines job.

Usage:
    ./manage.py sync_svrs_from_pe -h

"""


from django.core.management.base import BaseCommand

import os
from jobs.models import Job, SyncSvrsFromPEsParameters
from product_license.licensed_capability import CMPProvisioningEngineLicensedCapability
from product_license.license_service import LicenseService
from provisionengines.models import ProvisionEngine
from utilities.logger import ThreadLogger

os.environ["DJANGO_SETTINGS_MODULE"] = "settings"

logger = ThreadLogger(__name__)


class Command(BaseCommand):
    help = """Runs the CloudBolt sync servers from provision engines job.

Usage:
  python manage.py sync_svrs_from_pe <test-dir>

    """

    def handle(self, *args, **options):
        if not LicenseService().is_licensed(CMPProvisioningEngineLicensedCapability):
            logger.info("Provision engine feature not licensed, skipping.")
            return

        if not ProvisionEngine.objects.exists():
            logger.info("No provision engines defined, skipping.")
            return

        # no parameters are needed - if we pass no PE, the job will sync with
        # all of them
        job_params = SyncSvrsFromPEsParameters.objects.create()
        job_params.save()

        job = Job(job_parameters=job_params, type="sync_svrs_from_pe")
        job.save()
        logfile = job.get_log_file_path()

        logger.info("Created job: %s" % job)
        logger.info("Job log file: %s" % logfile)
        logger.info("Exiting")
