"""
Methods to popluate the data for the form
are stored in this module.
"""

from resourcehandlers.models import ResourceHandler


def generate_options_for_resource_handlers():
    rts = ResourceHandler.objects.all()
    # only Azure type RH
    for r in rts:
        if r.type_slug == "azure_arm":
            options = [(r.id, r.name)]

    return options
