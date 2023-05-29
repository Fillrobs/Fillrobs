import time

from common.methods import set_progress
from resourcehandlers.azure_arm.models import AzureARMHandler


def run(job, logger):
    """
    Rule action fetches and caches image data for all Azure Resource Manager resource handlers passed from the
    condition.

    Expects condition to pass a param 'locations_by_handler' that is
    a dict: {handler_id: [locations], ...}
    """
    params = job.job_parameters.cast().arguments

    str_to_bool = {"True": True, "False": False}
    use_whitelist = str_to_bool.get("{{ use_whitelist }}", False)
    set_progress("The parameter 'use_whitelist' is set to {}.".format(use_whitelist))

    errors = []  # noqa: F841
    handlers = params["locations_by_handler"]
    for handler_id, locations in list(handlers.items()):
        handler = AzureARMHandler.objects.get(id=handler_id)
        if use_whitelist:
            set_progress(
                'Fetching whitelisted images for Azure Resource Manager handler "{}". '.format(
                    handler
                )
            )
        else:
            set_progress(
                'Fetching all available images for Azure Resource Manager handler "{}". '
                "This may take 20 or more minutes without a whitelist. ".format(handler)
            )

        # Enumerating these so we can skip the first, since we only want to sleep on subsequent locations.
        for i, location in enumerate(locations):
            if i > 0 and not use_whitelist:
                set_progress(
                    "Sleeping for 30 minutes to avoid exceeding API rate limit. (15K/hr)"
                )
                time.sleep(30 * 60)

            if use_whitelist:
                set_progress('\nWorking on location "{}".'.format(location))
            else:
                set_progress(
                    'Working on location "{}". This may take 20 or more minutes.'.format(
                        location
                    )
                )

            try:
                images = handler.get_all_templates(
                    locations=[location],
                    force_refresh=True,
                    use_whitelist=use_whitelist,
                )
            except Exception as e:
                msg = f"Error while fetching images for handler {handler_id} and location {location}: {e}"
                job.set_progress(msg)

                return "FAILURE", "", ""

            set_progress(
                'There are now a total of {} images for location "{}".'.format(
                    len(images), location
                )
            )

    return "SUCCESS", "", ""
