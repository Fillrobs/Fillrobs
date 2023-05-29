"""
Recurring job to make sure there is always an Azure rate card cached in the
CloudBolt filesystem. Based on Azure's documented schedule for their billing
information, we recommend running this every 24 hours.
"""
from resourcehandlers.azure_arm.models import AzureARMHandler


def run(*_args, **_kwargs):
    """
    Entrypoint for a CloudBolt job: Find all Azure resource handlers in the
    system and ask them to download their rate cards.
    """
    for rh in AzureARMHandler.objects.all():
        rh: AzureARMHandler = rh.cast()
        rh.download_rate_card()  # defaults are fine
