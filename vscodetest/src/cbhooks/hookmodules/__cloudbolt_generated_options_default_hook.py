"""
Hook used to generate options for some out-of-the-box custom fields.

Must implement the get_options_list() that returns a list of
tuples like [(val1, display1), (val2, display2),...] or a list of CustomFieldValues.
"""
from django.conf import settings
from resourcehandlers.vmware.models import VmwareDisk
from utilities.models import LDAPUtility


def get_options_list(field, environment=None, group=None, **kwargs):
    """
    Default method for the ootb values_locked and dynamic cfs:
    vmware_disk_type, aws_elastic_ip, domain_to_join, time_zone, and more

    `kwargs` is there to ignore any additional parameters that are added to the
    signature of this method later that we do not care about.
    """
    server = kwargs.get("server", None)

    options = []

    if field.type == "LDAP":
        options = get_ldap_options_list(field, environment, group)
    elif field.name == "vmware_disk_type":
        options = get_vmware_disk_type_options_list(field, environment, group, server)
    elif field.name == "time_zone":
        options = get_time_zone_options_list(field, environment, group)
    elif field.name == "aws_elastic_ip":
        options = get_aws_elastic_ip_options_list(field, environment, group)
    elif field.name == "os_floating_ip":
        options = get_os_floating_ip_options_list(field, environment, group)
    elif field.name == "oracle_ip_reservation":
        options = get_oracle_ip_reservations_list(field, environment, group)

    return options


def get_ldap_options_list(field, environment, group):
    choices = []
    for ldap_utility in LDAPUtility.objects.all():
        choices.append((ldap_utility, ldap_utility.ldap_domain))
    return choices


def get_vmware_disk_type_options_list(field, environment, group, server=None):
    choices = []
    for prov_type, prov_type_display in VmwareDisk.PROV_TYPE_CHOICES:
        choices.append((prov_type_display, prov_type_display))
    return choices


def get_time_zone_options_list(field, environment, group):
    return [(tz, tz) for _, tz in settings.TZ_CHOICES]


def get_aws_elastic_ip_options_list(field, environment, group):
    if environment:
        rh = environment.resource_handler
        if rh:
            aws = rh.cast()
            return aws.options_for_aws_elastic_ip(field, environment)
    return []


def get_os_floating_ip_options_list(field, environment, group):
    if environment:
        rh = environment.resource_handler
        if rh:
            openstack = rh.cast()
            return openstack.get_floating_ip_options(
                openstack.get_env_location(environment)
            )
    return []


def get_oracle_ip_reservations_list(field, environment, group):
    if environment:
        rh = environment.resource_handler
        if rh:
            oracle = rh.cast()
            w = oracle.get_api_wrapper()
            ppips = w.get_ip_reservations(permanent=True, used=False)

            ip_reservations = [
                (None, "None"),
                ("ippool:/oracle/public/ippool", "Auto Generated"),
            ]

            # Add ppips to ip_reservations
            for ppip in ppips:
                ip_reservations.append((ppip["name"].split("/")[-1], ppip["ip"]))

            return ip_reservations

    return []
