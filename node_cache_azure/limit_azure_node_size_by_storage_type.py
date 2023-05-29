import re
from orders.models import CustomFieldValue
from infrastructure.models import Environment
from resourcehandlers.azure_arm.models import AzureARMHandler
import json, os
from django.conf import settings
from utilities.logger import ThreadLogger
from json.decoder import JSONDecodeError

logger = ThreadLogger(__name__)

NODE_SIZE_CACHE = os.path.join(settings.PROSERV_DIR, "azure_node_sizes.json")

class JsonCache():
    def __init__(self):
        if os.path.exists(NODE_SIZE_CACHE):
            self.load()
        else:
            self.data = {}

    def load(self):
        with open(NODE_SIZE_CACHE) as f:
            try:
                self.data = json.load(f)
            except JSONDecodeError as e:
                logger.info("Removing node_size_cache as it is invalid json")
                os.unlink(NODE_SIZE_CACHE)
                self.data = {}

    def save(self):
        with open(NODE_SIZE_CACHE, "w") as f:
            f.write(json.dumps(self.data, indent=4))

    def get(self, key):
        return self.data.get(key, None)

    def set(self, key, value, timeout=None):
        # we just look like the cache api
        # we don't implement timeout here
        self.data[key] = value

def _cache_key(node_size):
    return f"azure_node_size-{node_size}"

def get_options_details(options):
    cache = JsonCache()

    detailed_options = []
    for val, name in options:
        cache_val = cache.get(_cache_key(val))
        # set cores and mem to unknown values in case cache_val is not set
        #   (so name gets set for visual clue to order from that there's a problem)
        cores = "?"
        mem = "?"
        if cache_val:
            cores, mem = cache_val.split("_")

        detailed_name = f'{name} (CPU cores: {cores} RAM: {mem}GB)'
        detailed_options.append((val, detailed_name))

    return detailed_options


def get_options_list(
    field, control_value=None, form_data=None, form_prefix=None, **kwargs
):
    """
    Regenerate options for Azure Node Size on the order form based on what storage option is selected.
    """
    options = []
    environment = kwargs.get("environment")

    if not environment and form_data:
        environment_key = form_prefix + "-environment"
        environment_id = form_data.get(environment_key, None)
        if isinstance(environment_id, list):
            environment_id = environment_id[0]
        environment = (
            Environment.objects.get(id=int(environment_id)) if environment_id else None
        )

    unfiltered_options = [
        (x.value, x.value)
        for x in CustomFieldValue.objects.filter(field=field, environment=environment)
    ]
    if control_value is not None and control_value == "Premium_LRS":
        """
        According to https://docs.microsoft.com/en-us/azure/virtual-machines/disks-types?toc=/azure/virtual-machines/linux/toc.json&bc=/azure/virtual-machines/linux/breadcrumb/toc.json,
        "to learn more about individual VM types and sizes in Azure for Windows or Linux, including which sizes are
        premium storage-compatible, see Sizes for virtual machines in Azure
        (https://docs.microsoft.com/en-us/azure/virtual-machines/sizes). From this article, you need to check each
        individual VM size article to determine if it is premium storage-compatible."
        The list of sizes below that can be selected with premium storage were determined from doing just that.
        """
        for option in unfiltered_options:
            # B-series
            if re.match(r"^(.*_B\d+.*)$", option[0]):
                options += [option]
            # DS-series, DSv2-series
            elif re.match(r"^(.*_DS\d+.*)$", option[0]):
                options += [option]
            # Dsv3-series, Dsv4-series, Dasv4-series, Ddsv4-series, DCsv2-series
            elif re.match(r"^(.*_D.*s_.*)$", option[0]):
                options += [option]
            # Esv3-series, Esv4-series, Easv4-series, Edsv4-series
            elif re.match(r"^(.*_E.*s_.*)$", option[0]):
                options += [option]
            # FS-series
            elif re.match(r"^(.*_FS\d+.*)$", option[0]):
                options += [option]
            # Fsv2-series
            elif re.match(r"^(.*_F\d+s_.*)$", option[0]):
                options += [option]
            # GS-Series
            elif re.match(r"^(.*_GS\d+.*)$", option[0]):
                options += [option]
            # HB-Series, original and v2
            elif re.match(r"^(.*_HB\d+.*)$", option[0]):
                options += [option]
            # HC-Series
            elif re.match(r"^(.*_HC\d+.*)$", option[0]):
                options += [option]
            # Lsv2-series
            elif re.match(r"^(.*_L\d+s_.*)$", option[0]):
                options += [option]
            # M-Series, original and v2
            elif re.match(r"^(.*_M\d+.*)$", option[0]):
                options += [option]
            # NC-series, v2 and v3 but not original, plus NCasT4_v3-series
            elif re.match(r"^(.*_NC\d+.*_v\d+)$", option[0]):
                options += [option]
            # ND-series, original and v2
            elif re.match(r"^(.*_ND\d+.*)$", option[0]):
                options += [option]
            # NV-series, v2, v3, and v4 but not original
            elif re.match(r"^(.*_NV\d+.*_v\d+)$", option[0]):
                options += [option]
    else:
        options = unfiltered_options

    options = get_options_details(options)

    return {
        "options": options,
        "override": True,
        "initial_value": options[0] if len(options) > 0 else "",
    }