"""
Gets the latest invoice for all Azure ARM RH's with Public cloud environment.
Uses the Azure Invoice Download API and to get the file and download it.
The invoice is to be accessible from the resource handler Overview tab.
"""
from azure.mgmt.billing.models import ErrorResponseException

from resourcehandlers.azure_arm.models import AzureARMHandler
from utilities.exceptions import CloudBoltException
from utilities.logger import ThreadLogger

logger = ThreadLogger(__name__)


def run(*args, **kwds):
    """
    Iterate over all Azure resource handlers and allow for each to fail gracefully
    without failing the entire job; if one fails, then only use a 'warning' status
    in case others succeed, and present the errors/exceptions.
    """
    status = "SUCCESS"
    output = ""
    errors = ""

    all_rhs = AzureARMHandler.objects.filter(cloud_environment="PUBLIC")

    for rh in all_rhs:
        try:
            rh.download_invoice()
            output += "\nSuccessfully downloaded invoice for Resource Handler: {rh}.".format(
                rh=rh
            )
        except ErrorResponseException as e:
            # We see miscrosoft-specific issues for things like an unsupported subscription type,
            # so just warn the user with this information, but don't fail the whole job.
            logger.exception(e)
            status = "WARNING"
            errors += "\nCould not download invoice for Resource Handler: {rh}.".format(
                rh=rh
            )
            continue
        except CloudBoltException as e:
            logger.exception(e)
            status = "FAILURE"
            errors += str(e)
            continue
        except Exception as e:
            # For unexpected exceptions, we will fail the job, but still continue to run on all RHs.
            logger.exception(e)
            status = "FAILURE"
            errors += "Unexpected error occurred while trying to fetch invoice for {rh}.".format(
                rh=rh
            )
            continue

    return status, output, errors


if __name__ == "__main__":
    """
    For testing, call this directly like so:
        python download_azure_invoices.py
    """
    import django

    django.setup()
    run()
