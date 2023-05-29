from utilities.logger import ThreadLogger


logger = ThreadLogger(__name__)


def get_options_list(field, server=None, **kwargs):
    """
    Restrict options for azure storage account type based on the context;
    Ultra Disks can only be used as Data disks, so
    if this is a new server provisioning order (indicated when server=None),
    then the user cannot use an UltraSSD_LRS storage type.
    Otherwise, when there is a server, we are on the form for adding a new
    data disk to an existing server, so make this option available.

    Note that other restrictions apply to the UltraSSD_LRS storage option that
    we have no validation for:
    https://docs.microsoft.com/en-us/azure/virtual-machines/windows/disks-enable-ultra-ssd
    Are only supported on the following VM series:
        ESv3, DSv3, FSv2, M, Mv2
    Also restricted to only a few regions / availability zones.
    """
    options = []
    environment = kwargs.get("environment")

    if environment:
        options = environment.custom_field_options.filter(field=field)

    if not server:
        options = options.exclude(str_value="UltraSSD_LRS")

    options = [(option.value, option.value) for option in options]

    return options
