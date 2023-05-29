from common.methods import set_progress
from resourcehandlers.azure_arm.models import AzureARMHandler


def check(job, logger):
    """
    Rule fetches image data for all Azure Resource Manager resource handlers. This enables
    the image import dialog on the resource handler detail page to run much
    faster, since the 20 minutes' delay is done asynchronously.
    """
    handlers = AzureARMHandler.objects.all()
    if handlers:
        locations_by_handler = {}
        for handler in handlers:
            locations_by_handler[handler.id] = list(handler.current_locations())

            set_progress(
                "Fetching all available images for {} locations in Azure Resource Manager handler {}. ".format(
                    len(locations_by_handler[handler.id]), handler
                )
            )

        return ("SUCCESS", "", "", dict(locations_by_handler=locations_by_handler))
    else:
        return ("SUCCESS", "", "", None)
