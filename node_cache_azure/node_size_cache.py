from resourcehandlers.azure_arm.models import AzureARMHandler
from orders.models import CustomFieldValue
from common.methods import set_progress
import json, os
from django.conf import settings
from utilities.logger import ThreadLogger
from json.decoder import JSONDecodeError

logger = ThreadLogger(__name__)

location = 'eastus'
rh = AzureARMHandler.objects.first()


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

def cache_node_size_details(node_sizes):
    """
    Requires at least 1 Azure Resource Handler already configured to complete successfully.
    Lookup the cores and memory for each Azure Node size, create a cache entry using the Node Size (key) and
    Cores_Memory (value) for future fast lookups and display on the order form.
    """
    w = rh.get_api_wrapper()
    client = w.compute_client

    cache = JsonCache()

    # node_sizes are idempotent so cache forever but check cache is fully populated
    needfetch = False
    for node_size in node_sizes:
        logger.info(f"checking node_size: {node_size}")
        if not cache.get(_cache_key(node_size)):
            needfetch = True
            break
    if not needfetch:
        set_progress("Cached fully populated")
        return

    seen = []
    skus = client.client.resource_skus.list()
    for sku in skus:
        if sku.resource_type != 'virtualMachines':
            continue
        if sku.name in seen:
            continue
        # just populate all skus this is very little storage

        cores = 0
        mem = 0
        for cap in sku.as_dict().get('capabilities',{}):
            if cap.get('name') == 'vCPUs':
                cores = cap.get('value')
            elif cap.get('name') == 'MemoryGB':
                mem = cap.get('value')

        cache_val = f'{cores}_{mem}'
        set_progress(f'Setting cache for node size {sku.name} = {cache_val}')
        cache.set(_cache_key(sku.name), cache_val, None)  # None => cache forever
        seen.append(sku.name)
        cache.save()

def run(job, **kwargs):
    if rh:
        node_sizes = CustomFieldValue.objects.filter(field__name='node_size').values_list('str_value', flat=True).distinct()
        cache_node_size_details(node_sizes)
        return "", "", ""
    else:
        msg = "An Azure Resource Handler has not yet been configured."
        return "WARNING", msg, msg
