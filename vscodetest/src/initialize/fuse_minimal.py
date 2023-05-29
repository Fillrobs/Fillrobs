import c2_wrapper
from accounts.models import (
    Group,
    GroupType,
    Role,
    UserProfile,
    CBPermission,
)
from product_license.eula.services import EULAService
from utilities.models import GlobalPreferences

GROUP_TYPE_WORKSPACE = "Workspace"
DEFAULT_WORKSPACE_NAME = "Default"
WORKSPACE_ROLES = [
    {
        "name": "admin",
        "label": "Workspace Admin",
        "description": "Ability to manage workspace users and content",
        "assignable_to_users": True,
        "permissions": [
            "module.view",
            "group.manage_members",
            "group.create_subgroup",
            "policy.list",
            "policy.execute",
            "policy.manage",
        ],
    },
    {
        "name": "member",
        "label": "Workspace Member",
        "description": "Ability to manage workspace content like policies",
        "assignable_to_users": True,
        "permissions": [
            "module.view",
            "policy.list",
            "policy.manage",
            "policy.execute",
        ],
    },
    {
        "name": "executor",
        "label": "Workspace Executor",
        "description": "Ability to execute policies",
        "assignable_to_users": True,
        "permissions": ["module.view", "policy.list", "policy.execute"],
    },
    {
        "name": "viewer",
        "label": "Workspace Viewer",
        "description": "Ability to view workspace content",
        "assignable_to_users": True,
        "permissions": ["module.view"],
    },
]

ADMIN_PERMISSIONS = [
    {
        "name": "policy.list",
        "label": "List Policies",
        "description": "Allows the user to list all policies",
    },
    {
        "name": "policy.manage",
        "label": "Manage Policies",
        "description": "Allows the user to manage all policies",
    },
    {
        "name": "policy.execute",
        "label": "Execute Policies",
        "description": "Allows the user to execute all policies",
    },
]

all_permissions = [
    {
        "name": "module.view",
        "label": "View Modules",
        "description": "Allows the user to view modules",
    }
]

hook_points = [
    {
        "name": "resource_actions",
        "label": "Resource Actions",
        "description": "List of custom resource actions.",
    },
]

hooks = [
    {
        "name": "Delete Resource",
        "description": "Delete all servers in the resource and mark the resource as historical.",
        "hook_point": "resource_actions",
        "module": "cbhooks/hookmodules/delete_resource.py",
        "enabled": True,
        "hook_point_attributes": {
            "label": "Delete",
            "extra_classes": "icon-delete",
            "dialog_message": "This will delete all servers in the resource and then mark the "
            "resource as historical.",
            "submit_button_label": "Delete",
        },
    },
]


def create_workspace_grouptype() -> GroupType:
    workspace_grouptype = GroupType.objects.filter(group_type=GROUP_TYPE_WORKSPACE)
    if not workspace_grouptype.exists():
        grouptype = GroupType.objects.create(group_type=GROUP_TYPE_WORKSPACE)
        return grouptype
    else:
        return workspace_grouptype.first()


def create_default_workspace(workspace_grouptype: GroupType) -> Group:
    default_workspaces = Group.objects.filter(type__group_type=GROUP_TYPE_WORKSPACE)
    if not default_workspaces.exists():
        default_workspace = Group.objects.get_or_create(
            name=DEFAULT_WORKSPACE_NAME, type=workspace_grouptype
        )
        return default_workspace
    else:
        return default_workspaces.first()


def create_workspace_roles(workspace_grouptype: GroupType):
    # Create the role and assign to group
    for role_dict in WORKSPACE_ROLES:
        c2_wrapper.create_role(role_dict, force_create_permissions=True)

    Group.objects.get_or_create(name="Default", type=workspace_grouptype)


def create_workspace_policy_permissions():
    """
    Helper method to create policy list, execute, manage permissions.
    """
    policy_permissions_list = []
    for permission in ADMIN_PERMISSIONS:
        policy_permissions_list.append(
            CBPermission(
                name=permission["name"],
                label=permission["label"],
                description=permission["description"],
            )
        )

    CBPermission.objects.bulk_create(policy_permissions_list, ignore_conflicts=True)


def initialize_fuse_items():
    workspace_grouptype = create_workspace_grouptype()
    create_workspace_policy_permissions()
    create_workspace_roles(workspace_grouptype)
    default_workspace = create_default_workspace(workspace_grouptype)

    # either this is a fresh install or someone deleted all workspace admins
    # we make the first admin in the system an admin in the default workspace then
    if not default_workspace.has_user_in_role("admin"):
        p = UserProfile.objects.filter(super_admin=True).first()
        if p:
            role = Role.objects.get(name="admin")
            p.add_role_for_group(role, default_workspace)

    EULAService.create()

    # Add OneFuse Blueprint Category to be used when filtering Blueprint-based Modules
    from tags.models import CloudBoltTag

    tag, _ = CloudBoltTag.objects.get_or_create(
        name="OneFuse", parent=None, sequence=0, model_name="serviceblueprint"
    )


def run_external_create_routines():
    """
    Wrapper for initializing Fuse items, which is what causes them to get created by create_objects
    """

    initialize_fuse_items()

    # bypass quick_setup since that is a CMP-specific workflow
    gp, _ = GlobalPreferences.objects.get_or_create()
    gp.run_quick_setup = False
    gp.save()
