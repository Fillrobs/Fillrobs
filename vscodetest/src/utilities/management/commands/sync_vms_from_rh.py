#!/usr/local/bin/python
from __future__ import unicode_literals

"""
django-admin command for synchronizing VMs from the resource handler(s).

For example, to import VMS from.............:
    ./manage.py sync_vms_from_rh ................

"""


from django.core.management.base import BaseCommand

import sys
import os
import logging
from jobs.models import Job, SyncVMParameters
from resourcehandlers.models import ResourceHandler
from utilities.logger import ThreadLogger

os.environ["DJANGO_SETTINGS_MODULE"] = "settings"


# FIXME There has got to be a better way of finding the CB dir than this:
mydir = os.path.abspath(os.path.dirname(__file__))
cloudbolt_rootdir = os.path.dirname(os.path.dirname(os.path.dirname(mydir)))

# Not sure why this is needed:
sys.path.insert(0, cloudbolt_rootdir)
cloudbolt_parentdir = os.path.dirname(cloudbolt_rootdir)
sys.path.insert(0, cloudbolt_parentdir)

logger = ThreadLogger(__name__)


def configure_logging(filename):
    """
    Configure the logger such that all run-time output, either emitted directly
    from this script or indirectly via the CloudBolt machinery, is captured
    *here* and does not pollute the application logs.
    """
    if filename:
        # Direct all output to the specified file
        handler = logging.handlers.RotatingFileHandler(
            filename, mode="a", maxBytes=1024 * 1024, backupCount=3
        )
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        )
        level = logging.DEBUG  # Capture debug output during the cron job

    else:
        # Direct all output to the console
        handler = logging.StreamHandler(stream=sys.stdout)
        formatter = logging.Formatter("%(message)s")
        level = logging.INFO  # Minimize debug output on the console

    handler.setLevel(level)
    handler.setFormatter(formatter)

    # Configure the top-level (root) logger with these settings
    logger.handlers = []  # @@disable handlers inherited from settings.py
    logger.setLevel(level)

    # FIXME for some reason adding this handler will print log messages twice,
    # so for now just adding it when a specific log file is requested:
    if filename:
        logger.addHandler(handler)

    return


def create_pending_sync_job(rh_name=None):
    """
    Kicks off a new sync vms job and returns this job object.  When rh_name is
    given, vms are synced from that rh only.
    """

    if not rh_name or rh_name == "all":
        # Sync all RHs:
        rhs = ResourceHandler.objects.all()
        rhs = [rh.cast() for rh in rhs]

        logger.info(
            "Found %s RHs total. The sync job will filter out any that "
            "do not support VM sync." % len(rhs)
        )
    else:
        # Sync only the specified RH:
        try:
            rh = ResourceHandler.objects.get(name=rh_name)
        except ResourceHandler.DoesNotExist:
            names = [rh.name for rh in ResourceHandler.objects.all()]
            msg = (
                "Could not find the specified resource handler.  "
                "Valid resource handler names: %s" % names
            )
            logger.error(msg)
            raise RuntimeError(msg)
        except ResourceHandler.MultipleObjectsReturned:
            msg = 'Multiple resource handlers exist in CB with name: "%s"!' % rh_name
            raise RuntimeError(msg)
        rhs = [rh.cast()]

    # NOTE: If create is True, the SyncVMsClass will use the following defaults for options:
    # user: admin
    # group: Unassigned
    # environment: Unassigned-<resource-handler>

    job_params = SyncVMParameters.objects.create()
    job_params.resource_handlers.set(rhs)
    job_params.save()

    job = Job(
        type="syncvms",
        job_parameters=job_params,
        # owner=profile,  # NOTE: command-line jobs have no owner
    )
    job.save()

    return job


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "-r",
            "--resource-handler",
            help="Resource Handler to import VMs from (optional). By default all resources handlers are scanned.",
        )

    help = """Creates or updates server records in CloudBolt for each VMs from the given resource handler.

Examples:
  python manage.py sync_vms_from_rh -r "vCenter 5"

  python manage.py sync_vms_from_rh --resource-handler "Xen"

  python manage.py sync_vms_from_rh

    """

    def handle(self, *args, **options):

        rh_name = options["resource_handler"]

        sync_job = create_pending_sync_job(rh_name)

        job_id = sync_job.id
        logfile = sync_job.get_log_file_path()

        logger.info("Created job: %s" % job_id)
        logger.info("Job log file: %s" % logfile)
        logger.info("Exiting")
