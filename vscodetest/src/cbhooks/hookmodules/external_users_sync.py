#!/usr/bin/env python

"""
A hook that will update (creating when needed) group membership and permissions
based on the user's LDAP settings, as well as setting attributes in LDAP as CFVs on UserProfiles.

OUs will become CloudBolt groups, membership on special LDAP groups:
CB-Requestors, CB-Approvers, CB-GroupManagers and CB-ResourceManagers will
dictate the permissions users will get on the cloudbolt group that matches the
user's current OU. This script assumes the default roles have not been renamed
or deleted.

Because in CloudBolt group names are unique today, this hook
will not create a group for any OU that already matches a group in CB.  Users
for that OU will still be created but will have no permissions set.
"""
from __future__ import print_function

from collections import defaultdict
import sys

if __name__ == "__main__":
    import django

    django.setup()

from django.utils.html import format_html, mark_safe

from accounts.models import (
    GroupRoleMembership,
    UserProfile,
    ExternalUserAttributeMapping,
)
from common.methods import is_cb_admin_enabled
from utilities.logger import ThreadLogger
from utilities.models import LDAPMapping
from utilities.templatetags.helper_tags import render_link

logger = ThreadLogger(__name__)


def run(job, mapping=None, dry_run=False, **kwargs):
    logger.debug("Running hook {}".format(__name__))

    users = kwargs.get("users", None)
    output = mark_safe("")
    if dry_run:
        output += mark_safe(
            "<p>This is a dry run. No permissions have actually changed.</p>"
        )
    verbose_output = len(users) == 1
    for user_profile in users:
        # Skip sync if user's LDAPUtility has no group or attribute mappings configured.
        if (
            not user_profile.ldap.ldapmapping_set.exists()
            and not user_profile.ldap.externaluserattributemapping_set.exists()
        ):
            continue

        logger.debug("Fetching external data for user: {}".format(user_profile))

        results = user_profile.ldap.runUserSearch(user_profile.user.username, find=[])
        if not results:
            return (
                "FAILURE",
                "",
                "LDAP query of {} did not find user {}.".format(
                    user_profile.ldap, user_profile.user.username
                ),
            )
        user_dn, user_data = results[0]
        # Both `sync_groups_for_user` and `sync_attrs_for_user` return SafeText,
        # so we're able to append them together.
        output += sync_groups_for_user(
            user_dn, user_data, user_profile, mapping, dry_run, verbose_output
        )
        output += sync_attrs_for_user(user_data, user_profile, dry_run, verbose_output)

    if len(users) > 1:
        output += format_html("{count} users were synced.", count=len(users))

    return "SUCCESS", output, ""


def sync_attrs_for_user(user_data, user_profile, dry_run, verbose_output):
    """
    For each ExternalUserAttributeMapping for this LDAP utility, check if that attribute is part
    of the user data. If so, set it on the user profile. This would typically be set as a custom
    field value on the user profile.

    Limitation: unlike syncing groups, this will not remove attrs for mappings that have been
    removed.

    :return An output string summarizing with a list of the attributes set and a summary (only
    if verbose_output is True, otherwise return "")
    """
    output = mark_safe("")
    mappings = ExternalUserAttributeMapping.objects.filter(
        ldap_utility=user_profile.ldap
    )
    if not mappings:
        if verbose_output:
            output += mark_safe(
                "No attribute mappings found for this LDAP Utility, skipping attribute mapping.<BR>"
            )
        return output
    updated_cnt = 0
    for mapping in mappings:
        external_value = user_data.get(mapping.external_attribute, "")
        if isinstance(external_value, list) or isinstance(external_value, tuple):
            # LDAP returns most values as one-item lists. In this case, extract the single value.
            if len(external_value) == 1:
                external_value = external_value[0]
        if external_value:
            if not dry_run:
                # Using setattr will work for setting CFVs as well as setting regular model fields.
                setattr(user_profile, mapping.cloudbolt_attribute, external_value)
            if verbose_output:
                output += format_html(
                    "Set {} to {}<BR>", mapping.cloudbolt_attribute, external_value
                )
            updated_cnt += 1
    if verbose_output:
        output += format_html("<p>{} attributes updated.</p>", updated_cnt)
    return output


def sync_groups_for_user(
    user_dn, user_data, user_profile, mapping, dry_run, verbose_output
):
    output = mark_safe("")
    # Get the distinguished name of the user's OUs and groups
    ldap_ou_dns = get_ou_dns(user_dn)
    ldap_group_dns = get_group_dns(user_data)

    # Get all mappings that match the user's OUs/groups/LDAPUtility
    # Include mappings configured to match "Any"
    mappings = LDAPMapping.get_mappings(
        utility=user_profile.ldap,
        ldap_group_dns=ldap_group_dns,
        ldap_ou_dns=ldap_ou_dns,
    )
    if mapping:
        mappings = mappings.filter(id=mapping.id)

    # Use mappings to determine which Group/Role combinations the user
    # should be given memberships in, and/or which global roles they should
    # receive.
    all_memberships = []
    # If they have the global role on any mapping, they will end up with it
    is_super_admin = False
    is_cbadmin = False
    is_devops_admin = False
    is_global_viewer = False
    has_api_access = False
    for m in mappings:  # use "m" to avoid clobbering "mapping"
        is_super_admin = is_super_admin or m.is_super_admin
        is_cbadmin = is_cbadmin or m.is_cbadmin
        is_devops_admin = is_devops_admin or m.is_devops_admin
        is_global_viewer = is_global_viewer or m.is_global_viewer
        has_api_access = has_api_access or m.has_api_access
        memberships = m.get_memberships(profile=user_profile)
        all_memberships.extend(memberships)
        if verbose_output:
            output = output_for_user(
                user_profile,
                all_memberships,
                is_cbadmin,
                is_super_admin,
                is_devops_admin,
                is_global_viewer,
                has_api_access,
            )

    if not dry_run:
        user_profile.super_admin = is_super_admin
        user_profile.devops_admin = is_devops_admin
        user_profile.global_viewer = is_global_viewer
        user_profile.api_access = has_api_access
        user_profile.save()
        user_profile.user.is_superuser = is_cbadmin
        user_profile.user.save()
        # Delete all existing group memberships and add the new ones
        user_profile.grouprolemembership_set.all().delete()
        GroupRoleMembership.objects.bulk_create(all_memberships)
    return output


def get_ou_dns(dn):
    """Given a user's DN, return the DN of any ancestor that is an OU."""
    ou_dns = []
    while dn:
        if dn.startswith("OU="):
            ou_dns.append(dn)
        parts = dn.split(",", 1)
        dn = parts[1] if len(parts) == 2 else ""

    logger.debug("User belongs to the following OU:")
    if ou_dns:
        # Only log the deepest OU
        logger.debug("  {}".format(ou_dns[0]))

    return ou_dns


def get_group_dns(user_data):
    """Return the DN of all groups that the user belongs to."""
    ldap_group_dns = user_data.get("memberOf", [])

    logger.debug("User belongs to the following group(s):")
    for group in ldap_group_dns:
        logger.debug("  {}".format(group))

        # it is possible our bytes_to_text implementation was unable to decode
        # the response from the LDAP server, in these cases it returns the
        # original bytestring. There is a decent chance the LDAP server gave us
        # text in the Windows_1252 encoding, so we give that a shot.
        if isinstance(group, bytes):
            logger.debug(
                "The above is a bytestring that could not be decoded to utf-8: {}. "
                "Attempting to decode to WINDOWS_1252".format(group)
            )
            try:
                decoded = group.decode("WINDOWS_1252")
                logger.debug("Successfully decoded to WINDOWS_1252")
            except UnicodeDecodeError:
                logger.debug("Unable to decode the above group, continuing.")
                ldap_group_dns.remove(group)
                continue
            ldap_group_dns.remove(group)
            ldap_group_dns.append(decoded)

    return ldap_group_dns


def output_for_user(
    profile,
    memberships,
    is_cbadmin,
    is_super_admin,
    is_devops_admin,
    is_global_viewer,
    has_api_access,
):
    """
    Show the sync output for a single user.
    """
    roles = mark_safe("")
    if is_cbadmin and is_cb_admin_enabled():
        roles += mark_safe("<li><b>CB Admin</b></li>")
    if is_super_admin:
        roles += mark_safe("<li><b>Super Admin</b></li>")
    if is_devops_admin:
        roles += mark_safe("<li><b>Devops Admin</b></li>")
    if is_global_viewer:
        roles += mark_safe("<li><b>Global Viewer</b></li>")
    if has_api_access:
        roles += mark_safe("<li><b>API Access</b></li>")

    roles_by_group = defaultdict(list)
    for m in memberships:
        roles_by_group[m.group].append(m.role)
    for group, role_list in roles_by_group.items():
        role_list_str = ", ".join(str(role) for role in role_list)
        roles += format_html("<li>{}: {}</li>", group, role_list_str)

    if not roles:
        roles = mark_safe("<li>No roles</li>")

    user = render_link(profile)
    logger.debug(roles)
    return format_html(
        "<p>{user} has the following roles after syncing:</p><ul>{roles}</ul>",
        user=user,
        roles=roles,
    )


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.stderr.write("usage: %s <CloudBolt UserProfile.username>\n" % (sys.argv[0]))
        sys.exit(2)
    username = sys.argv[1]
    try:
        profile = UserProfile.objects.get(user__username=username)
    except:  # noqa: E722
        print("Failed to fetch user with username: {}".format(username))
        exit(1)
    status, msg, err = run(None, None, users=[profile])
    print("status, msg, err = {} {} {}".format(status, msg, err))
