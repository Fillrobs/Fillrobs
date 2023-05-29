from connectors.puppet_ent import api_wrapper
from connectors.puppet_ent.exceptions import PEApiException
from utilities.logger import ThreadLogger

logger = ThreadLogger(__name__)


def get_node_facts(**kwargs):
    """
    Get node facts for all nodes that match 'certnames' passed in kwargs.  If no certnames, this
    method queries all active certnames known to the puppet master instance.
    """

    peconf = kwargs.get("peconf", None)
    certnames = kwargs.get("certnames", None)
    certnames = certnames or api_wrapper.get_certnames(peconf)

    all_facts = []
    for certname in certnames:
        try:
            facts = api_wrapper.get_node_facts(peconf, certname)
            all_facts.append(facts)
        except PEApiException:
            pass
        except Exception:
            logger.exception(
                "An exception occurred when getting node facts for {}".format(certname)
            )
            pass

    return all_facts
