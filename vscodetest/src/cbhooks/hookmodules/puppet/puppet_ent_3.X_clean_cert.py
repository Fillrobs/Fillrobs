from connectors.puppet_ent import api_wrapper
from utilities.logger import ThreadLogger

logger = ThreadLogger(__name__)


def clean_cert(**kwargs):
    """
    Delete from the puppet master any node that matches 'certname' passed in kwargs.
    """

    peconf = kwargs.get("peconf", None)
    certname = kwargs.get("certname", None)

    api_wrapper.delete_node(peconf, certname)
