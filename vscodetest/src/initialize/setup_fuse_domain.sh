#!/bin/bash

echo "Setting up Domain Provider for 1F"

read -p 'Domain: ' DOMAIN
read -p "FQDN or IP of Directory Server: " HOST
read -p "Protocol [ldap or ldaps]: " PROTO
PROTO=${PROTO:-ldap}
read -p "Port [389]: " PORT
PORT=${PORT:-389}
read -p "Domain Authentication Account [user@domain]: " ACCT

unset PASS
PASS_PROMPT="Domain Authentication Password: "
while IFS= read -p "$PASS_PROMPT"  -r -s -n 1 char
do
    if [[ $char == $'\0' ]]
    then
        break
    fi
    PASS_PROMPT='*'
    PASS="${PASS}${char}"
done
echo ""
read -p "Base DN: " BASE_DN

echo "User attribute mappings ..."
read -p "Username [sAMAccountName]: " USERNAME
USERNAME=${USERNAME:-sAMAccountName}
read -p "Fist Name [givenName]: " FIRST
FIRST=${FIRST:-givenName}
read -p "Last Name [sn]: " LAST
LAST=${LAST:-sn}
read -p "Email [mail]: " MAIL
MAIL=${MAIL:-mail}

echo "Domain RBAC mappings..."
read -p 'Group DN for Workspace Admins: ' ADMIN_GROUP_DN
read -p 'Group DN for Workspace Members: ' MEMBER_GROUP_DN
read -p 'Group DN for Workspace Executors: ' EXECUTOR_GROUP_DN
read -p 'Group DN for Workspace Viewers: ' VIEWER_GROUP_DN


echo "Compiling LDAP configurations for Execution..."

cat <<EOF > /tmp/domain_setup.py
from accounts.models import Group, Role
from product_license.methods import is_personality_fuse
from utilities.models import LDAPUtility, LDAPMapping, LDAPMappingGroup

hook_points = [
    {
        "name": "external_users_sync",
        "label": "External Users Sync",
        "description": (
            "Executes whenever external users synchronization takes "
            "place, including each time an external user logs in."
        ),
    }
]

hooks = [
    {
        "name": "User Permission Sync From LDAP",
        "description": (
            "Updates user's permissions in CloudBolt based on the user's LDAP "
            "permissions. Configure how LDAP groups and OUs map to CloudBolt "
            "Groups and Roles on the LDAP settings page."
        ),
        "hook_point": "external_users_sync",
        "module": "cbhooks/hookmodules/external_users_sync.py",
        "enabled": True,
        # give existing actions priority by putting this action before them
        "hook_point_attributes": {"run_seq": 1},
    },
]

def run_external_create_routines():
    """
    Wrapper for initializing Fuse items, which is what causes them to get created by create_objects
    """

    if not is_personality_fuse():
        print("This helper script is meant to be run on OneFuse licensed appliances only!")
        print("To setup domains in the CMP, please use the product interface.")
        return

    LDAP_UTILITY = {
        "ldap_domain": "$DOMAIN",
        "serviceaccount": "$ACCT",
        "servicepasswd": "$PASS",
        "ip": "$HOST",
        "protocol": "$PROTO",
        "port": $PORT,
        "ldap_first": "$FIRST",
        "ldap_last": "$LAST",
        "ldap_username": "$USERNAME",
        "ldap_mail": "$MAIL",
        "base_dn": "$BASE_DN",
        "auto_create_user": True
    }

    WORKSPACE_ADMIN_SECURITY_GROUP_DN = "$ADMIN_GROUP_DN"
    WORKSPACE_MEMBER_SECURITY_GROUP_DN = "$MEMBER_GROUP_DN"
    WORKSPACE_EXECUTOR_SECURITY_GROUP_DN = "$EXECUTOR_GROUP_DN"
    WORKSPACE_VIEWER_SECURITY_GROUP_DN = "$VIEWER_GROUP_DN"

    domain = LDAP_UTILITY.pop("ldap_domain")
    ldap, _ = LDAPUtility.objects.get_or_create(ldap_domain=domain, defaults=LDAP_UTILITY)

    group = Group.objects.get(name="Default", type__group_type="Workspace")

    if WORKSPACE_ADMIN_SECURITY_GROUP_DN:
        map = LDAPMapping(ldap_utility=ldap)
        map.ldap_group_dn = WORKSPACE_ADMIN_SECURITY_GROUP_DN
        map.save()
        gm = LDAPMappingGroup(mapping=map, group=group)
        gm.save()
        gm.roles.add(Role.objects.get(label="Workspace Admin"))

    if WORKSPACE_MEMBER_SECURITY_GROUP_DN:
        map = LDAPMapping(ldap_utility=ldap)
        map.ldap_group_dn = WORKSPACE_MEMBER_SECURITY_GROUP_DN
        map.save()
        gm = LDAPMappingGroup(mapping=map, group=group)
        gm.save()
        gm.roles.add(Role.objects.get(label="Workspace Member"))

    if WORKSPACE_EXECUTOR_SECURITY_GROUP_DN:
        map = LDAPMapping(ldap_utility=ldap)
        map.ldap_group_dn = WORKSPACE_EXECUTOR_SECURITY_GROUP_DN
        map.save()
        gm = LDAPMappingGroup(mapping=map, group=group)
        gm.roles.add(Role.objects.get(label="Workspace Executor"))

    if WORKSPACE_VIEWER_SECURITY_GROUP_DN:
        map = LDAPMapping(ldap_utility=ldap)
        map.ldap_group_dn = WORKSPACE_VIEWER_SECURITY_GROUP_DN
        map.save()
        gm = LDAPMappingGroup(mapping=map, group=group)
        gm.save()
        gm.roles.add(Role.objects.get(label="Workspace Viewer"))


EOF

echo "Creating LDAP mappings..."
/opt/cloudbolt/initialize/create_objects.py /tmp/domain_setup.py

rm -f /tmp/domain_setup.py

echo "LDAP configuration complete"
