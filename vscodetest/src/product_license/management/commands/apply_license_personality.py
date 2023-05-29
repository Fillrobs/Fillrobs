from django.core.management.base import BaseCommand

from jobs.models import Job, JobParameters
from product_license.license_service import LicenseService


class Command(BaseCommand):
    help = (
        "Apply the correct personality based on the license file.  It will either run the 'Apply"
        " Personality Job' (preferred) or attempt to perform the same tasks without a job record ("
        "useful when a job engine is not available)"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "-t",
            "--timeout",
            default=120,
            help=(
                "Timeout for the Apply Personality Job (if running as a job), in seconds [%default]"
            ),
        )

        parser.add_argument(
            "-n",
            "--no-job",
            action="store_true",
            default=False,
            help="If specified it will NOT create a job record of this execution",
        )

    def handle(self, *args, **options):
        """
        Actually call the appropriate tool to apply the personality, either via the Job or directly using
        the method on CloudBoltLicense (which is what the Job calls)
        """

        as_job = not options["no_job"]
        timeout = int(options["timeout"])

        if as_job:
            # Creates a back-end Job to apply the personality
            # NOTE: we don't need to actually use the JobParameters to store anything, which is
            # why they're generic and empty, but the Job model requires having something there
            job = Job.objects.create(
                type="apply_personality",
                job_parameters=JobParameters.objects.create(),
                status="PENDING",
            )
            job.wait_for_completion(timeout=timeout)
        else:
            LicenseService().apply_personality()
