#!/usr/bin/env python

"""
Handles updating a user based on data returned from a Single Sign-On (SSO)
Identity Provider (IdP) as part of the login process for SSO. This hook can
be updated to handle any extra data you track in your SSO and map it to the
appropriate values for a given User.
"""

from typing import Any, Optional

from django.utils.translation import gettext as _

from accounts.models import User
from authentication.sso.models import BaseSSOProvider
from authentication.sso.services import SSOInterface
from jobs.models import Job
from utilities.logger import ThreadLogger
from utilities.models import LDAPUtility

logger = ThreadLogger(__name__)

LDAP_DOMAIN_SSO_ATTR_NAME = "ldapDomain"


def run(
    job: Optional[Job] = None,
    user: Optional[User] = None,
    attrs_from_sso: Optional[dict] = None,
    sso_instance: Optional[BaseSSOProvider] = None,
    creating: bool = False,
    **kwargs,
):
    """Update the input user based on `attrs_from_sso` from the SSO IdP

    :param job: Not used, but all hooks need to take this an as argument
    :param user: User object
    :param attrs_from_sso: dict, attribute names and values from the SSO IdP
    :param sso_instance: BaseSSOProvider object, or child class
    :param creating: bool, True if the User was just created, False otherwise
    :param kwargs: dict, anything else passed to this hook
    :return: Tuple[str, str, str] Status, Output, Errors
    """
    logger.debug("Running hook {}".format(__name__))
    # make sure we have a User
    if not user:
        msg = _("No 'user' passed to hook 'SSO User Update.' Exiting...")
        logger.error(msg)
        return "FAILURE", "", msg
    # make sure the User is up-to-date
    user.refresh_from_db()
    # make sure we have data from the SSO
    if not attrs_from_sso:
        msg = _("No 'attrs_from_sso' passed to hook 'SSO User Update.' Exiting...")
        logger.error(msg)
        return "FAILURE", "", msg
    # special handling for the username in case it includes a domain: ie user@domain.com
    username, ldap_domain_name = None, None
    if sso_instance.user_attribute_uid in attrs_from_sso:
        full_username: str = _get_first_item_if_list(
            attrs_from_sso[sso_instance.user_attribute_uid]
        )
        if "@" in full_username:
            username, ldap_domain_name = SSOInterface.split_username_and_domain(
                full_username
            )

    # make the dict of User attributes to update
    # `user_attr_map` will be dict mapping user attribute name to the value received from
    # the SSO IdP for this attribute
    # for example {"first_name": "My New First Name"}
    user_attr_map: dict = SSOInterface.generate_user_attr_map(
        sso_instance, attrs_from_sso
    )
    # if we are handling the username specially and it is in the user_attr_map
    # then make sure to include the value with the domain name removed
    if username and "username" in user_attr_map:
        user_attr_map["username"] = username
    # try to update the User
    updated = _update_obj(user, **user_attr_map)
    # dict and function that can be edited to update a User's profile
    profile_attrs_to_update = {}
    updated |= _update_obj(user.userprofile, **profile_attrs_to_update)
    if not ldap_domain_name:
        ldap_domain_name = _get_ldap_domain_name(sso_instance, attrs_from_sso)
    # try to update the LDAPUtility on the UserProfile of the User
    if ldap_domain_name:
        updated |= _update_ldap_domain(user, ldap_domain_name)
    if updated:
        msg = _("User '{user}' updated.".format(user=user.username))
    else:
        msg = _("No updates required for User '{user}'.".format(user=user.username))
    return "SUCCESS", msg, ""


def _get_first_item_if_list(value: Any) -> Any:
    """Returns `value` or the first item of `value` if `value is a list"""
    if isinstance(value, list) and len(value) > 0:
        return value[0]
    return value


def _update_obj(obj: Any, **kwargs) -> bool:
    """Update the various attributes of a an object using kwargs and return a bool

    :param obj: object to update
    :param kwargs: key-value pairs of attributes to update on try to update User
    :return: bool, True if object successfully updated, False otherwise
    """
    updated: bool = False
    for attr_name, new_value in kwargs.items():
        # |= operator is a logical OR equals
        # equivalent to `update = updated or _attr_update(...)`
        # once it is True, it stays True
        updated |= _attr_update(obj, attr_name, new_value)
    if updated:
        # if the object was updated and has a save method, then save it
        try:
            obj.save()
        except (AttributeError, TypeError):
            pass
    return updated


def _attr_update(obj_to_update: Any, attr_name: str, new_value: Any) -> bool:
    """Try to update the given attribute on the given object and return a bool

    :param obj_to_update: the object to update
    :param attr_name: str, the name of the attribute to update
    :param new_value: the new value for the attribute
    :return: bool, True if attribute was updated, False otherwise
    """
    try:
        current_value = getattr(obj_to_update, attr_name)
    except AttributeError as e:
        msg = _(
            f"Cannot update attr '{attr_name}' on '{obj_to_update}' because the attribute does not exist."
        )
        logger.exception(msg)
        raise AttributeError(msg) from e

    is_changed: bool = (current_value != new_value) and (bool(new_value))
    if is_changed:
        setattr(obj_to_update, attr_name, new_value)
    # invert the return b/c it is more intuitive for True to mean that the user WAS updated
    return is_changed


def _get_ldap_domain_name(
    sso_instance: BaseSSOProvider,
    attrs_from_sso: dict,
    ldap_domain_attr_name: Optional[str] = None,
) -> Optional[str]:
    # set default name for LDAP domain attribute, if necessary
    if not ldap_domain_attr_name:
        ldap_domain_attr_name = LDAP_DOMAIN_SSO_ATTR_NAME
    # get the LDAP domain from the attribute
    ldap_domain_name = _get_first_item_if_list(
        attrs_from_sso.get(ldap_domain_attr_name, None)
    )
    # if attrs_from_sso doesn't have the ldap domain name attribute
    if not ldap_domain_name:
        # and we can't get the domain name from the username, then return False
        sso_username_attr = sso_instance.user_attribute_uid
        full_username: str = attrs_from_sso.get(sso_username_attr)
        if full_username:
            __, ldap_domain_name = SSOInterface.split_username_and_domain(full_username)
    return ldap_domain_name


def _update_ldap_domain(user: User, ldap_domain_name: str,) -> bool:
    """Update UserProfile with LDAPUtility, if matching LDAPUtility is found

    :return: bool, True if UserProfile update with new LDAPUtility, False otherwise
    """
    try:
        ldap_utility = LDAPUtility.objects.get(ldap_domain=ldap_domain_name)
    except LDAPUtility.DoesNotExist:
        # log an error and return if we don't find a matching LDAPUtility
        msg = _("LDAPUtility for domain '{domain_name}' does not exist")
        logger.error(msg.format(domain_name=ldap_domain_name))
        return False
    # update the user's UserProfile with the LDAP and save
    updated: bool = _attr_update(user.userprofile, "ldap", ldap_utility)
    if updated:
        user.userprofile.save()
    return updated
