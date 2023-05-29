"""
Hook for deleting a server from LDAP during a server delete job

Only unregisters the server from LDAP on the Domain Controller, rather than
actually changing the server itself to remove it from the domain.

Note: Before using this hook, make sure that you have a suitable LDAP Utility
created in the Admin/LDAP Authentication Settings page. It can determine the
LDAP Utility to remove from in a couple different ways. The best option might be
to have the Domain to Join parameter set. Another is to have the DNS Domain
field in the network information for the pertinent resource handler matching the
LDAP Domain field of an LDAP Utility. If you do not configure either of those,
but have only one LDAP Utility, that will be used as a default.
"""
from __future__ import print_function

import ldap
import os

os.environ["DJANGO_SETTINGS_MODULE"] = "settings"
import sys

sys.path.append("/opt/cloudbolt")
from utilities.logger import ThreadLogger

logger = ThreadLogger(__name__)
from utilities.admin import LDAPUtility


def ldap_bind(ldapurl, ldapuser, ldappass):
    """
    Initializes and binds the ldap_module in order to work with it
    """
    ldap_module = ldap.initialize(ldapurl)
    # Do not require certificate verification
    ldap_module.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
    ldap_module.set_option(ldap.OPT_X_TLS_NEWCTX, 0)  # Must force new context
    ldap_module.simple_bind_s(ldapuser, ldappass)
    return ldap_module


def ldap_unbind(ldap_module):
    """
    Unbinds the ldap_module once we are done with it
    """
    try:
        ldap_module.unbind_s()
    except ldap.LDAPError as err:
        print(err)


def ldap_search(computer, ldapbasedn, ldap_module):
    """
    Finds the given computer in LDAP if it exists
    """
    searchscope = ldap.SCOPE_SUBTREE
    retrieveattrs = ["dn", "cn", "dnshostname"]
    searchfilter = "(&(objectclass=computer)(cn={}))".format(computer)
    ldap_result = ldap_module.search_ext_s(
        ldapbasedn, searchscope, searchfilter, retrieveattrs, sizelimit=1
    )
    result2dict = dict(ldap_result)
    keys = list(result2dict.keys())
    if not keys:  # To prevent error if not found in LDAP
        return False
    dn = keys[0]
    return dn


def ldap_delete(deletedn, ldap_module):
    """
    Deletes the computer entry from LDAP, unregistering it
    """
    try:
        ldap_module.delete_s(deletedn)
    except ldap.LDAPError as err:
        print(err)


def get_ldaputility(server):
    """
    Determines the LDAPUtility associated with the given server. Tries a couple
    different approaches to have the best chance of successfully finding one
    """
    # If server has domain_to_join set use that
    ldaputility = server.domain_to_join
    # Second option: match network's DNS Domain
    if not ldaputility:
        network = server.nics.first().network
        if network:
            ldaputility = LDAPUtility.objects.filter(
                ldap_domain=network.dns_domain
            ).first()
    # If the others don't work, and there's only 1 LDAPUtility, use it
    if not ldaputility:
        if LDAPUtility.objects.count() == 1:
            ldaputility = LDAPUtility.objects.first()
    return ldaputility


def run(job, *args, **kwargs):
    server_records = job.server_set.all()
    for server in server_records:
        # Try to determine computer name
        computer = server.hostname.split(".")[0]
        if not computer:
            job.set_progress("Unable to determine computer name for this server")
            continue
        # Try to find LDAPUtility for server
        ldaputility = get_ldaputility(server)
        if not ldaputility:
            job.set_progress("Server not associated with LDAP in CB")
            continue
        ldapuser = ldaputility.serviceaccount
        ldappass = ldaputility.servicepasswd
        ldapserver = ldaputility.ip
        ldapport = ldaputility.port
        if ldapport == 389:
            ldapurl = "ldap://{}:{}".format(ldapserver, ldapport)
        elif ldapport == 636:
            ldapurl = "ldaps://{}:{}".format(ldapserver, ldapport)
        ldapbasedn = ldaputility.base_dn
        # Look for computer in LDAP, delete if found
        bind = ldap_bind(ldapurl, ldapuser, ldappass)
        logger.info('Searching for AD computer object "{}"'.format(computer))
        searchdn = ldap_search(computer, ldapbasedn, bind)
        if not searchdn:
            job.set_progress("Computer does not appear to be in LDAP")
            continue
        logger.info('Found object DN  : "{}"'.format(searchdn))
        logger.info('Delete object DN : "{}"'.format(searchdn))
        ldap_delete(searchdn, bind)
        ldap_unbind(bind)
        job.set_progress('Computer object "{}" has been deleted'.format(computer))
    return "", "", ""


if __name__ == "__main__":
    job_id = sys.argv[1]
    from jobs.models import Job

    job = Job.objects.get(id=job_id)
    print(run(job))
