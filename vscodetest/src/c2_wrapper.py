#!/usr/bin/env python
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import os
import shutil
import sys
import time
from tempfile import mkdtemp
from typing import List

cloudbolt_rootdir = os.path.abspath(os.path.dirname(__file__))
c2_parent_dir = os.path.dirname(cloudbolt_rootdir)
sys.path.insert(0, c2_parent_dir)

if "DJANGO_SETTINGS_MODULE" not in os.environ:
    os.environ["DJANGO_SETTINGS_MODULE"] = "settings"

if __name__ == "__main__":
    import django

    django.setup()

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files import File
from django.db.models import F

from accounts.models import Group, GroupRoleMembership, GroupType, Role, CBPermission
from behavior_mapping.models import CustomFieldMapping
from cbadmin.models import StaticPage
from cbhooks.models import (
    HookPoint,
    HookPointAction,
    CloudBoltHook,
    TriggerPoint,
    HookInput,
    RunHookInputMapping,
    ResourceAction,
    ServerAction,
    RemoteScriptHook,
    IPAMHook,
    DataProtectionHook,
    ServiceNowHook,
    ITSMHook,
)
from dataprotection.models import DataProtectionTechnology
from externalcontent.models import Application, OSBuild, OSFamily
from infrastructure.models import (
    CustomField,
    DataCenter,
    Environment,
    Namespace,
    Preconfiguration,
    ResourcePool,
    ResourcePoolValueSet,
)
from ipam.models import IPAMTechnology
from itsm.models import ITSMTechnology
from jobs.models import Job
from networks.models import LoadBalancerTechnology
from network_virtualization.models import NetworkVirtualizationTechnology
from orchestrationengines.models import (
    OrchestrationTechnology,
    OrchestrationFlow,
    OrchestrationFlowParameters,
)
from orchestrationengines.hpoo.models import HPOO
from orders.models import (
    CustomFieldValue,
    DecomServerOrderItem,
    Order,
    PreconfigurationValueSet,
    ProvisionServerOrderItem,
)
from portals.models import PortalConfig
from provisionengines.models import ProvisionTechnology
from provisionengines.razor.models import RazorServer
from reportengines.jasper.models import JasperReportingEngine
from resourcehandlers.models import ResourceTechnology, ResourceNetwork
from resourcehandlers.aws.models import AmazonMachineImage, AWSHandler
from resourcehandlers.openstack.models import OpenStackHandler
from resourcehandlers.qemu.models import QemuOSBuildAttribute, QemuResourceHandler
from resourcehandlers.slayer.models import SlayerOSBuildAttribute
from resourcehandlers.vmware.models import (
    VmwareNetwork,
    VsphereOSBuildAttribute,
    VsphereResourceHandler,
)
from resourcehandlers.xen.models import (
    XenNetwork,
    XenOSBuildAttribute,
    XenResourceHandler,
)
from servicecatalog.models import ServiceBlueprint
from utilities.exceptions import TimeoutException
from utilities.models import GlobalPreferences

debug = False
predebug = "c2_wrapper: "


def guess_os_family(image_dict):
    """
    Return an appropriate OSFamily object given an image_dict as
    returned from get_all_templates.  Return None if no match is
    found.  Searches several dict members for possible matches.
    """
    alt_names = OSFamily.get_alt_names_by_family()

    for key in ["name", "description", "guest_os"]:
        val = (image_dict.get(key) or "").lower()
        if val:
            # Search the OSFamily table for a match by name, going from
            # more specific ('Ubuntu') to less specific ('Linux').
            # This is better than hard-coding heuristic tests here because
            # it enables new families to be supported as soon as they're
            # added to the OSFamily model (by an admin user, for example).
            for family, names in list(alt_names.items()):
                for name in names:
                    if val.find(name.lower()) != -1:
                        # print('Guessed family {} from image_dict[{}]'.format(family, key))
                        return family

    # the only unique platform value is 'windows'
    platform = image_dict.get("platform", "")
    if platform and platform.lower() == "windows":
        return OSFamily.objects.get(name="Windows")

    return None


def create_user(username, first_name, last_name, email, password):
    user, created = User.objects.get_or_create(
        username=username,
        defaults={"first_name": first_name, "last_name": last_name, "email": email},
    )
    if debug and created:
        print(
            '%sCreated New User named "%s" (first: %s, last: %s, email: %s) [id: %s]'
            % (predebug, user.username, first_name, last_name, email, user.id)
        )
    if debug and not created:
        print(
            '%sUser named "%s" already exists [id: %s]'
            % (predebug, user.username, user.id)
        )

    user.set_password(password)
    user.save()
    if debug:
        print(
            '%sPassword for User "%s" set to "%s"' % (predebug, user.username, password)
        )
    profile = user.userprofile
    profile.save()

    return user


def grant_super_admin(user):
    # This must be set to allow the admin user to accept the OneFuse EULA if OneFuse is
    # the first product to have a license activated.
    user.userprofile.super_admin = True
    user.userprofile.save()
    if debug:
        print(
            '%sGranted Super Admin privileges to User "%s" [id: %s]'
            % (predebug, user.username, user.id)
        )


def grant_cbadmin(user):
    # is_superuser means "CB Admin"
    user.is_superuser = True
    user.save()
    if debug:
        print(
            '%sGranted CB Admin privileges to User "%s" [id: %s]'
            % (predebug, user.username, user.id)
        )


def grant_staff(user):
    user.is_staff = True
    user.save()
    if debug:
        print(
            '%sGranted staff privileges to User "%s" [id: %s]'
            % (predebug, user.username, user.id)
        )


def create_cbadmin(username, first_name, last_name, password, email):
    super_user = create_user(
        username=username,
        first_name=first_name,
        last_name=last_name,
        password=password,
        email=email,
    )
    grant_cbadmin(super_user)
    grant_staff(super_user)

    return super_user


def create_group_type(group_type):
    group_type, created = GroupType.objects.get_or_create(group_type=group_type)
    if debug:
        if not created:
            print(
                '%sReused GroupType "%s" [id: %s]'
                % (predebug, group_type, group_type.id)
            )
        else:
            print(
                '%sCreated GroupType "%s" [id: %s]'
                % (predebug, group_type, group_type.id)
            )
    return group_type


def create_cloudbolt_group(group_dict):
    group_type = create_group_type(group_dict["type"])
    group, created = Group.objects.get_or_create(
        name=group_dict["name"], defaults={"type": group_type}
    )
    if not created and group.type != group_type:
        print("     Updating type from %s to %s" % (group.type, group_type))
        group.type = group_type
        group.save()

    if "parent" in group_dict:
        if group_dict["parent"]:
            groupparent = Group.objects.get(name=group_dict["parent"])
            group.parent = groupparent
            group.save()
            if debug:
                print(
                    '%sAttached Group "%s" to parent "%s"'
                    % (predebug, group.name, group.parent)
                )

    if "levels_to_show" in group_dict:
        group.levels_to_show = group_dict["levels_to_show"]
        group.save()

    if "environments" in group_dict:
        for environment in group_dict["environments"]:
            attach_environment_to_group(environment, group)

    # if 'quota' in group_dict:
    #    for key, val in group_dict['quota'].items():
    #        create_basic_quota_item(key, val, group)

    if "cfos" in group_dict:
        for custom_field in list(group_dict["cfos"].keys()):
            for value in group_dict["cfos"][custom_field]:
                cfv = create_custom_field_value(custom_field, value)
                attach_custom_field_option(group, cfv)
                attach_custom_field(object=group, custom_field_name=custom_field)

    return group


def grant_cloudbolt_group_priv(group_name, group_privs, user):
    try:
        group = Group.objects.get(name=group_name)
    except Group.DoesNotExist:
        # Bad test fixture?  Create a group on the fly.
        group = Group.objects.create(name=group_name, type=GroupType.objects.first())

    for user_perm in group_privs:
        role, _ = Role.objects.get_or_create(name=user_perm)
        GroupRoleMembership.objects.get_or_create(
            group=group, role=role, profile=user.userprofile
        )
        if debug:
            print(
                '%sGranted "%s" privileges to user "%s" on Group "%s"'
                % (predebug, user_perm, user, group)
            )
    return group


def create_role(role_dict, force_create_permissions=False):
    role_dict = role_dict.copy()  # prevent modifications to the original
    permissions = role_dict.pop("permissions", [])
    role, created = Role.objects.get_or_create(
        name=role_dict["name"], defaults=role_dict
    )
    if created or force_create_permissions:
        cb_permissions = CBPermission.objects.filter(name__in=permissions)
        role.permissions.add(*cb_permissions)

    return role


def create_resource_pool(dict):
    if "include_mac" not in dict:
        dict["include_mac"] = False
    resource_pool = ResourcePool.objects.create(
        include_hostname=dict["include_hostname"],
        include_ipaddress=dict["include_ipaddress"],
        include_mac=dict["include_mac"],
    )

    name = dict.get("name")
    if name:
        resource_pool.name = name
        resource_pool.save()

    for rpvs_dict in dict["rows"]:
        create_resource_pool_value_set(
            resource_pool,
            rpvs_dict,
            # hostname = rpvs_dict['hostname'],
            # ip = rpvs_dict['ip'],
        )

    if debug:
        print("%sCreated ResourcePool [id: %s]" % (predebug, resource_pool.id))
    return resource_pool


def create_resource_pool_value_set(resource_pool, nvpair_dict):
    rpvs = ResourcePoolValueSet.objects.create(
        resource_pool=resource_pool, **nvpair_dict
    )
    if debug:
        print(
            "%sCreated ResourcePoolValueSet (%s) [id: %s]"
            % (predebug, nvpair_dict, rpvs.id)
        )
    return rpvs


def create_xen_network(name, network, vlan):
    xen_network, created = XenNetwork.objects.get_or_create(
        name=name, network=network, vlan=vlan
    )
    if debug:
        if not created:
            print(
                '%sReused XenNetwork named "%s" (network: %s, vlan: %s) [id: %s]'
                % (predebug, name, network, vlan, xen_network.id)
            )
        else:
            print(
                '%sCreated XenNetwork named "%s" (network: %s, vlan: %s) [id: %s]'
                % (predebug, name, network, vlan, xen_network.id)
            )
    return xen_network


def create_vmware_network(
    name,
    dvSwitch,
    network,
    vlan,
    adapterType,
    addressing_schema,
    gateway,
    netmask,
    dns1=None,
    dns2=None,
):
    vmware_networks = VmwareNetwork.objects.filter(name=name)
    if len(vmware_networks) > 0:
        # shouldn't be > 1, but it is on .185 now
        vmware_network = vmware_networks[0]
    else:
        vmware_network = VmwareNetwork.objects.create(name=name)
    vmware_network.dvSwitch = dvSwitch
    vmware_network.network = network
    vmware_network.vlan = vlan
    vmware_network.adapterType = adapterType
    vmware_network.addressing_schema = addressing_schema
    vmware_network.gateway = gateway
    vmware_network.netmask = netmask
    vmware_network.dns1 = dns1
    vmware_network.dns2 = dns2
    vmware_network.save()

    if debug:
        print(
            '%sCreated/reused VmwareNetwork named "%s" (dvswitch: %s, network: %s, vlan: %s, adapter: %s) [id: %s]'
            % (predebug, name, dvSwitch, network, vlan, adapterType, vmware_network.id)
        )
    return vmware_network


def create_jasperreport_engine(
    host="localhost",
    port="8080",
    reports_path="/reports/cloudbolt",
    default_format="pdf",
    serviceaccount="jasperadmin",
    servicepasswd="jasperadmin",
    scheme="http",
):

    jasperreport_engine = JasperReportingEngine.objects.filter(
        host=host, port=port, serviceaccount=serviceaccount
    )

    if jasperreport_engine:
        jasperreport_engine = jasperreport_engine[0]
    else:
        jasperreport_engine = JasperReportingEngine.objects.create(
            host=host,
            port=port,
            reports_path=reports_path,
            default_format=default_format,
            serviceaccount=serviceaccount,
            servicepasswd=servicepasswd,
            scheme=scheme,
        )

        if debug:
            print(
                "%sCreated JasperReportingEngine "
                "(host: %s, port: %s, reports_path: %s, serviceaccount: %s, "
                "servicepasswd: %s, default_format: %s, scheme: %s) "
                "[id: %s]"
                % (
                    predebug,
                    host,
                    port,
                    reports_path,
                    serviceaccount,
                    servicepasswd,
                    default_format,
                    scheme,
                    jasperreport_engine.id,
                )
            )
    return jasperreport_engine


def create_hpoo_engine(dict, tech):
    hpoo = HPOO.objects.filter(
        host=dict["host"], serviceaccount=dict["serviceaccount"], technology=tech
    )
    if hpoo:
        if debug:
            print("%sFound HPOO engine: %s, reusing it..." % (hpoo[0]))
        hpoo = hpoo[0]
    else:
        if debug:
            print(
                "Creating HPOO engine [host:%s, account:%s]..."
                % (dict["host"], dict["serviceaccount"])
            )
        hpoo = HPOO.objects.create(
            host=dict["host"], serviceaccount=dict["serviceaccount"], technology=tech
        )
    hpoo.name = dict["name"]
    hpoo.servicepasswd = dict["servicepasswd"]
    hpoo.flow_repo_path = dict["flow_repo_path"]
    hpoo.save()

    if "flows" in dict:
        for flow_dict in dict["flows"]:
            create_or_update_flow(flow_dict, hpoo)


def create_or_update_flow(dict, engine):
    flow = OrchestrationFlow.objects.filter(
        name=dict["name"], uuid=dict["uuid"], engine=engine
    )
    if flow:
        flow = flow[0]

    else:
        flow = OrchestrationFlow.objects.create(uuid=dict["uuid"], engine=engine)
    flow.name = dict["name"]
    flow.expose_as_server_action = getattr(dict, "expose_as_server_action", False)
    flow.save()

    if "parameters" in dict:
        existing_params = OrchestrationFlowParameters.objects.filter(flow=flow)
        updated_params = []
        for param in dict["parameters"]:
            flow_param = None
            for ep in existing_params:
                if ep.param_key == param["key"]:
                    flow_param = ep
                    updated_params += [ep]
                    break
            if not flow_param:
                flow_param = OrchestrationFlowParameters(
                    param_key=param["key"], flow=flow
                )
            if "c2_mapping" in param:
                flow_param.param_c2_mapping = param["c2_mapping"]
            else:
                flow_param.param_c2_mapping = None
            if "required" in param:
                flow_param.param_required = param["required"]
            else:
                flow_param.param_required = False

            flow_param.save()
        for param in [p for p in existing_params if p not in updated_params]:
            param.delete()


def create_xen_resource_handler(
    name,
    ip,
    port,
    protocol,
    serviceaccount,
    servicepasswd,
    resource_technology,
    default_sr,
):
    xen_rh = XenResourceHandler.objects.filter(
        name=name, resource_technology=resource_technology, ip=ip
    )
    if xen_rh:
        xen_rh = xen_rh[0]
    else:
        xen_rh = XenResourceHandler.objects.create(
            name=name,
            ip=ip,
            port=port,
            protocol=protocol,
            serviceaccount=serviceaccount,
            servicepasswd=servicepasswd,
            resource_technology=resource_technology,
            default_sr=default_sr,
        )

        if debug:
            print(
                '%sCreated XenResourceHandler named "%s" (ip: %s, port: %s'
                ", protocol: %s, account: %s, password: %s, tech: %s, "
                "default_sr: %s) [id: %s]"
                % (
                    predebug,
                    name,
                    ip,
                    port,
                    protocol,
                    serviceaccount,
                    servicepasswd,
                    resource_technology,
                    default_sr,
                    xen_rh.id,
                )
            )
    return xen_rh


def create_qemu_resource_handler(
    name, ip, port, protocol, serviceaccount, servicepasswd, resource_technology
):
    qemu_rh = QemuResourceHandler.objects.filter(
        name=name, resource_technology=resource_technology, ip=ip
    )
    if qemu_rh:
        qemu_rh = qemu_rh[0]
    else:
        qemu_rh = QemuResourceHandler.objects.create(
            name=name,
            ip=ip,
            port=port,
            protocol=protocol,
            serviceaccount=serviceaccount,
            servicepasswd=servicepasswd,
            resource_technology=resource_technology,
        )

        if debug:
            print(
                '%sCreated QemuResourceHandler named "%s" (ip: %s, port: %s, protocol: %s, account: %s, password: %s, tech: %s) [id: %s]'
                % (
                    predebug,
                    name,
                    ip,
                    port,
                    protocol,
                    serviceaccount,
                    servicepasswd,
                    resource_technology,
                    qemu_rh.id,
                )
            )
    return qemu_rh


def create_aws_handler(name, resource_technology, attrdict):
    """
    This method will leave the resource handler alone if one exists with the
    same name and resource tech.  Otherwise it will create it.
    """
    aws_rh = AWSHandler.objects.filter(
        name=name, resource_technology=resource_technology
    )
    if aws_rh:
        aws_rh = aws_rh[0]
    else:
        aws_rh = AWSHandler.objects.create(
            resource_technology=resource_technology, **attrdict
        )
    return aws_rh


def create_openstack_handler(name, resource_technology, attrdict):
    """
    This method will leave the resource handler alone if one exists with the
    same name and resource tech.  Otherwise it will create it.
    """
    os_rh = OpenStackHandler.objects.filter(
        name=name, resource_technology=resource_technology
    )
    if os_rh:
        os_rh = os_rh[0]
    else:
        os_rh = OpenStackHandler.objects.create(
            resource_technology=resource_technology, **attrdict
        )
    return os_rh


def create_vsphere_resource_handler(name, ip, resource_technology, attrdict):

    vmware_rh = VsphereResourceHandler.objects.filter(
        name=name, ip=ip, resource_technology=resource_technology
    )
    if vmware_rh:
        vmware_rh = vmware_rh[0]
    else:
        vmware_rh = VsphereResourceHandler.objects.create(
            resource_technology=resource_technology, **attrdict
        )
    return vmware_rh


def create_resource_technology(rt_name, rt_version, rt_module, rt_slug=""):
    resource_technology, created = ResourceTechnology.objects.update_or_create(
        name=rt_name,
        defaults={"version": rt_version, "modulename": rt_module, "slug": rt_slug},
    )
    if debug:
        if not created:
            print(
                '%sReused ResourceTechnology named "%s" (version: %s, module: %s) [id: %s]'
                % (predebug, rt_name, rt_version, rt_module, resource_technology.id)
            )
        else:
            print(
                '%sCreated ResourceTechnology named "%s" (version: %s, module: %s) [id: %s]'
                % (predebug, rt_name, rt_version, rt_module, resource_technology.id)
            )
    return resource_technology


def create_global_preferences():
    if GlobalPreferences.objects.exists():
        return GlobalPreferences.get()

    gp = GlobalPreferences()

    gp.save()
    if debug:
        print("%sCreated GlobalPreferences" % (predebug))
    return gp


def set_smtp_prefs(host, port=25, tls=False, username="", password=""):
    gp = create_global_preferences()
    gp.smtp_host = host
    gp.smtp_port = port
    gp.smtp_user = username
    gp.smtp_password = password
    gp.smtp_use_tls = tls
    gp.save()


def is_group_type_order_filter_defined():
    gp = create_global_preferences()
    return gp.group_type_order_filter.exists()


def attach_group_type_to_gp(group_type):
    gt = create_group_type(group_type=group_type)
    gp = create_global_preferences()
    gp.group_type_order_filter.add(gt)
    gp.save()
    if debug:
        print('%sAttached group_type "%s" to GlobalPreferences' % (predebug, gt))
    return gp


def attach_environment_to_group(environment, group):
    g = Group.objects.get_or_create(name=group)[0]
    s = Environment.objects.get_or_create(name=environment)[0]

    # first, make the environment available to the project
    s.groups_served.add(g)
    s.save()

    # now update the project to select the environment as an available environment
    g.environments.add(s)
    g.save()
    if debug:
        print('%sAttached environment "%s" to group "%s"' % (predebug, s, g))
    return g


def create_environment(
    name, provision_engine, resource_handler, resource_pool=None, data_center_name=""
):
    """
    The default get_or_create() was creating duplicates when it should not have
    been, so we're implementing our own get_or_create()-like functionality here
    """
    created = 0
    dc = None
    if data_center_name:
        dc = DataCenter.objects.filter(name=data_center_name)[0]

    environments = Environment.objects.filter(name=name)
    if len(environments) > 1:
        raise Exception("Found more than one environment with name %s!" % name)
    if not environments:
        environment = Environment.objects.create(
            name=name,
            provision_engine=provision_engine,
            resource_handler=resource_handler,
            data_center=dc,
        )
        created = 1
    else:
        environment = environments[0]
        environment.provision_engine = provision_engine
        environment.resource_handler = resource_handler
        environment.data_center = dc
        environment.save()

    if debug:
        if not created:
            print(
                '%sReused Environment named "%s" (resource_handler: %s, provision_engine: %s) [id: %s]'
                % (predebug, name, resource_handler, provision_engine, environment.id)
            )
        else:
            print(
                '%sCreated Environment named "%s" (resource_handler: %s, provision_engine: %s) [id: %s]'
                % (predebug, name, resource_handler, provision_engine, environment.id)
            )
    if resource_pool:
        environment = attach_resource_pool_to_environment(environment, resource_pool)
    return environment


def attach_resource_pool_to_environment(environment, resource_pool):
    environment.resource_pool = resource_pool
    environment.save()
    if debug:
        print(
            '%sAttached ResourcePool "%s" to Environment "%s"'
            % (predebug, resource_pool, environment)
        )
    return environment


def create_provision_technology(name, version):
    provision_technology, created = ProvisionTechnology.objects.get_or_create(
        name=name, version=version
    )
    if debug:
        if not created:
            print(
                '%sReused ProvisionTechnology "%s" (version: %s) [id: %s]'
                % (predebug, name, version, provision_technology.id)
            )
        else:
            print(
                '%sCreated ProvisionTechnology "%s" (version: %s) [id: %s]'
                % (predebug, name, version, provision_technology.id)
            )
    return provision_technology


def create_ipam_technology(name, version, modulename):
    technology, created = IPAMTechnology.objects.get_or_create(
        name=name, version=version
    )
    technology.modulename = modulename
    technology.save()
    if debug:
        if not created:
            print(
                '%sReused IPAMTechnology "%s" (version: %s) [id: %s]'
                % (predebug, name, version, technology.id)
            )
        else:
            print(
                '%sCreated IPAMTechnology "%s" (version: %s) [id: %s]'
                % (predebug, name, version, technology.id)
            )
    return technology


def create_itsm_technology(name, version, modulename):
    technology, created = ITSMTechnology.objects.get_or_create(
        name=name, version=version
    )
    technology.modulename = modulename
    technology.save()
    if debug:
        if not created:
            print(
                '%sReused ITSMTechnology "%s" (version: %s) [id: %s]'
                % (predebug, name, version, technology.id)
            )
        else:
            print(
                '%sCreated ITSMTechnology "%s" (version: %s) [id: %s]'
                % (predebug, name, version, technology.id)
            )
    return technology


def create_network_virtualization_technology(name, version, modulename):
    technology, created = NetworkVirtualizationTechnology.objects.get_or_create(
        name=name, version=version
    )
    technology.modulename = modulename
    technology.save()
    if debug:
        action = "Reused" if not created else "Created"
        print(
            f'{ predebug }{ action } NetworkVirtualizationTechnology "{ name }" '
            f"(version: { version }) [id: { technology.id }]"
        )
    return technology


def create_orchestration_technology(name, version, modulename):
    technology, created = OrchestrationTechnology.objects.get_or_create(
        name=name, version=version
    )
    technology.modulename = modulename
    technology.save()
    if debug:
        if not created:
            print(
                '%sReused OrchestrationTechnology "%s" (version: %s) [id: %s]'
                % (predebug, name, version, technology.id)
            )
        else:
            print(
                '%sCreated OrchestrationTechnology "%s" (version: %s) [id: %s]'
                % (predebug, name, version, technology.id)
            )
    return technology


def create_provision_engine(
    name,
    ip=None,
    port=None,
    protocol=None,
    serviceaccount=None,
    servicepasswd=None,
    provision_technology=None,
):

    if name.find("Razor") != -1:
        pe_class = RazorServer
    else:
        msg = "Could not determine what type of Provision Engine to create "
        msg = msg + ("based on this name: %s" % name)
        raise Exception(msg)

    if not ip:
        # allow the config file to just specify the name, if it's
        # already been created
        return pe_class.objects.get(name)
    provision_engine = pe_class.objects.filter(
        name=name, ip=ip, provision_technology=provision_technology
    )
    if provision_engine:
        provision_engine = provision_engine[0]
    else:
        provision_engine = pe_class.objects.create(
            name=name,
            ip=ip,
            port=port,
            protocol=protocol,
            serviceaccount=serviceaccount,
            servicepasswd=servicepasswd,
            provision_technology=provision_technology,
        )
    if debug:
        print(
            '%sCreated/reused ProvisionEngine "%s" (ip: %s, port: %s, protocol: %s, serviceaccount: %s, servicepasswd: %s, provision_technology: %s) [id: %s]'
            % (
                predebug,
                name,
                ip,
                port,
                protocol,
                serviceaccount,
                servicepasswd,
                provision_technology,
                provision_engine.id,
            )
        )
    return provision_engine


def create_custom_field(
    name,
    label,
    type,
    required=False,
    namespace=None,
    show_on_servers=False,
    available_all_servers=False,
    show_as_attribute=False,
    description=None,
    global_constraints=None,
    allow_multiple=False,
):
    """
    If the global_constraints argument is passed in, it should be a dictionary
    of constraint values where the keys may include 'minimum', 'maximum' and
    'regex_constraint'.
    """
    if namespace:
        namespace = get_or_create_namespace(name=namespace)

    # Pass type as a default in case a customer has changed the CF from type STR to TXT, or INT to
    # DEC, CB should be okay with that and the upgrader should not fail out.
    custom_field, created = CustomField.objects.get_or_create(
        name=name,
        namespace=namespace,
        defaults={
            "type": type,
            "label": label,
            "required": required,
            "show_on_servers": show_on_servers,
            "available_all_servers": available_all_servers,
            "show_as_attribute": show_as_attribute,
            "allow_multiple": allow_multiple,
        },
    )

    # Description can change on existing CF
    custom_field.description = description
    custom_field.save()

    if global_constraints:
        # First look for a CFM that's currently used for global constraints, since that
        # lets us use the safest option of the global_constraints manager
        cfm = CustomFieldMapping.global_constraints.filter(
            custom_field=custom_field
        ).first()
        # If that doesn't find anything, try looking for one that may have been
        # previously used for global constraints (but not defaults)
        if cfm is None:
            # If this fails with "get() returned more than one CustomFieldMapping", check out
            # https://cloudbolt.atlassian.net/browse/DEV-20315
            cfm, __ = CustomFieldMapping.global_mappings_not_defaults.get_or_create(
                custom_field=custom_field
            )
        custom_field.set_constraints_in_cfm(cfm, global_constraints)

    if debug:
        if not created:
            print(
                '%sReused CustomField "%s" (label: %s, type: %s) [id: %s]'
                % (predebug, name, label, type, custom_field.id)
            )
        else:
            print(
                '%sCreated CustomField "%s" (label: %s, type: %s) [id: %s]'
                % (predebug, name, label, type, custom_field.id)
            )
    return custom_field


def create_field_dependencies(field_dependencies: List[dict], skip=None):
    """
    Creates a FieldDependency, a relationship between two CustomField objects.
    Optionally adds ControlValue objects, which provide a relationship with CustomFieldValue objects,
    which function for the dependency to only show when a certain value is entered on the controlling field.

    Assumes that the dependent and controlling fields already exist, because this should run after they've been created.

    :param field_dependencies: a list of dictionaries that must contain the keys 'dependent_field' and
    'controlling_field'. For example, see 'aws_field_dependencies' in 'aws_minimal.py'
    """
    from infrastructure.models import FieldDependency, ControlValue

    for dependency_dict in field_dependencies:
        # Gets the controlling field and the dependent field.
        controlling_field = CustomField.objects.get(
            **dependency_dict["controlling_field"]
        )
        dependent_field = CustomField.objects.get(**dependency_dict["dependent_field"])
        dependency_type = dependency_dict.get(
            "dependency_type", "SHOWHIDE"
        )  # default to SHOWHIDE if none specified.
        controlling_values = dependency_dict.get("controlling_values", [])

        # Set up the FieldDependency.
        fd, _ = FieldDependency.objects.get_or_create(
            controlling_field=controlling_field,
            dependent_field=dependent_field,
            dependency_type=dependency_type,
        )

        # Add any controlling values.
        for control_value in controlling_values:
            controlling_cfv, created = CustomFieldValue.objects.get_or_create(
                field=controlling_field, **control_value
            )
            ControlValue.objects.get_or_create(
                field_dependency=fd, custom_field_value=controlling_cfv
            )


def create_custom_field_options(field_name, options):
    # This seems to duplicate the logic in create_custom_field_value()

    cf = CustomField.objects.get(name=field_name)

    for option in options:
        cfv, created = CustomFieldValue.objects.get_or_create(field=cf, value=option)
        if debug:
            if not created:
                print(
                    '%sReused CustomFieldValue "%s" (field: %s) [id: %s]'
                    % (predebug, option, cf, cfv.id)
                )
            else:
                print(
                    '%sCreated CustomFieldValue "%s" (field: %s) [id: %s]'
                    % (predebug, option, cf, cfv.id)
                )


def create_custom_field_global_options(field_name, options):
    """
    Slightly different than the above. Creates options on the CF's CustomFieldMapping
    so that they are globally set.

    Assumes the CF with the field name getting passed in already exists
    """
    cf = CustomField.objects.get(name=field_name)
    cfm = cf.get_global_mapping()
    for option in options:
        cfv = create_custom_field_value(custom_field_name=cf.name, value=option)
        cfm.options.add(cfv)


def create_preconfiguration(name, label):
    preconfiguration, created = Preconfiguration.objects.get_or_create(name=name)
    if preconfiguration.label != label:
        preconfiguration.label = label
        preconfiguration.save()

    if debug:
        if not created:
            print(
                '%sReused Preconfiguration "%s" (label: %s) [id: %s]'
                % (predebug, name, label, preconfiguration.id)
            )
        else:
            print(
                '%sCreated Preconfiguration "%s" (label: %s) [id: %s]'
                % (predebug, name, label, preconfiguration.id)
            )
    if not created:
        # it already existed, return None to signal to the caller that it was pre-existing and
        # should not be modified
        return None
    return preconfiguration


def create_preconfiguration_value_set(value, preconfiguration, display_order=1):
    pcvs, created = PreconfigurationValueSet.objects.get_or_create(
        value=value, preconfiguration=preconfiguration, display_order=display_order
    )
    if debug:
        if not created:
            print(
                '%sReused PreconfigurationValueSet "%s" (preconfiguration: %s) [id: %s]'
                % (predebug, value, preconfiguration, pcvs.id)
            )
        else:
            print(
                '%sCreated PreconfigurationValueSet "%s" (preconfiguration: %s) [id: %s]'
                % (predebug, value, preconfiguration, pcvs.id)
            )

    if not created:
        # it already existed, return None to signal to the caller that it was pre-existing and
        # should not be modified
        return None
    return pcvs


def create_custom_field_value(custom_field_name, value):
    # This seems to duplicate the logic in create_custom_field_options()

    field = CustomField.objects.get(name=custom_field_name)
    custom_field_value, created = CustomFieldValue.objects.get_or_create(
        field=field, value=value
    )
    if debug:
        if not created:
            print(
                '%sReused CustomFieldValue "%s" [id: %s]'
                % (predebug, custom_field_value, custom_field_value.id)
            )
        else:
            print(
                '%sCreated CustomFieldValue "%s" (value: %s) [id: %s]'
                % (predebug, field, value, custom_field_value.id)
            )
    return custom_field_value


def create_osbuild(name, environments=None, template=False):
    osbuild, created = OSBuild.objects.get_or_create(name=name)
    if template:
        osbuild.use_handler_template = True
        osbuild.save()

    if debug:
        if not created:
            print('%sReused OSBuild named "%s" [id: %s]' % (predebug, name, osbuild.id))
        else:
            print(
                '%sCreated OSBuild named "%s" [id: %s]' % (predebug, name, osbuild.id)
            )
    return osbuild


def create_xen_osbuild_attributes(os_build, template_name):
    xen_osbuild_attribute, created = XenOSBuildAttribute.objects.get_or_create(
        os_build=os_build, template_name=template_name
    )
    if debug:
        if created:
            print(
                '%sReused XenOSBuildAttribute for OSBuild "%s" (template_name: %s) [id: %s]'
                % (predebug, os_build.name, template_name, xen_osbuild_attribute.id)
            )
        else:
            print(
                '%sCreated XenOSBuildAttribute for OSBuild "%s" (template_name: %s) [id: %s]'
                % (predebug, os_build.name, template_name, xen_osbuild_attribute.id)
            )
    return xen_osbuild_attribute


def create_slayer_osbuild_attributes(os_build, template_name, uuid):
    slayer_osbuild_attribute, created = SlayerOSBuildAttribute.objects.get_or_create(
        os_build=os_build, template_name=template_name, uuid=uuid
    )
    if debug:
        if created:
            print(
                '%sReused SlayerOSBuildAttribute for OSBuild "%s" (template_name: %s) [id: %s]'
                % (predebug, os_build.name, template_name, slayer_osbuild_attribute.id)
            )
        else:
            print(
                '%sCreated SlayerOSBuildAttribute for OSBuild "%s" (template_name: %s) [id: %s]'
                % (predebug, os_build.name, template_name, slayer_osbuild_attribute.id)
            )
    return slayer_osbuild_attribute


def create_qemu_osbuild_attributes(os_build, template_name):
    qemu_osbuild_attribute, created = QemuOSBuildAttribute.objects.get_or_create(
        os_build=os_build, template_name=template_name
    )
    if debug:
        if created:
            print(
                '%sReused QemuOSBuildAttribute for OSBuild "%s" (template_name: %s) [id: %s]'
                % (predebug, os_build.name, template_name, qemu_osbuild_attribute.id)
            )
        else:
            print(
                '%sCreated QemuOSBuildAttribute for OSBuild "%s" (template_name: %s) [id: %s]'
                % (predebug, os_build.name, template_name, qemu_osbuild_attribute.id)
            )
    return qemu_osbuild_attribute


def create_aws_osbuild_attributes(os_build, build_dict):
    ami, created = AmazonMachineImage.objects.get_or_create(
        os_build=os_build,
        ami_id=build_dict["ami_id"],
        region=build_dict.get("region"),
        is_public=build_dict.get("is_public"),
        owner_id=build_dict.get("owner_id"),
        root_device_type=build_dict.get("root_device_type"),
    )
    if debug:
        ami_id = build_dict["ami_id"]
        if created:
            print("%sCreated AMI %s" % (predebug, ami_id))
        else:
            print("%sReused AMI %s" % (predebug, ami_id))
    return ami


def create_vsphere_osbuild_attributes(os_build, guest_id, template_name=None):
    vmware_osbuild_attributes = VsphereOSBuildAttribute.objects.filter(
        os_build=os_build, guest_id=guest_id, template_name=template_name
    )
    if vmware_osbuild_attributes:
        vmware_osbuild_attribute = vmware_osbuild_attributes[0]
        if debug:
            print(
                '%sReused VsphereOSBuildAttribute for OSBuild "%s" (guest_id: %s) [id: %s]'
                % (predebug, os_build.name, guest_id, vmware_osbuild_attribute.id)
            )
    else:
        vmware_osbuild_attribute = VsphereOSBuildAttribute.objects.create(
            os_build=os_build, guest_id=guest_id, template_name=template_name
        )
        if debug:
            print(
                '%sCreated VsphereOSBuildAttribute for OSBuild "%s" (guest_id: %s) [id: %s]'
                % (predebug, os_build.name, guest_id, vmware_osbuild_attribute.id)
            )
    return vmware_osbuild_attribute


def attach_osbuild_to_environment(osbuild, environment):
    osbuild.environments.add(environment)
    osbuild.save()
    if debug:
        print(
            '%sAttached Environment "%s" to OSBuild named "%s"'
            % (predebug, environment, osbuild.name)
        )


def create_application(name, environments=None):
    application, created = Application.objects.get_or_create(name=name)
    if debug:
        if not created:
            print(
                '%sReused Application named "%s" [id: %s]'
                % (predebug, name, application.id)
            )
        else:
            print(
                '%sCreated Application named "%s" [id: %s]'
                % (predebug, name, application.id)
            )
    return application


def attach_application_to_environment(application, environment):
    application.environments.add(environment)
    application.save()
    if debug:
        print(
            '%sAttached Environment "%s" to OSBuild named "%s"'
            % (predebug, environment, application.name)
        )


def attach_network_to_handler(handler, network):
    handler.networks.add(network)
    handler.save()
    if debug:
        print(
            '%sAttached VmwareNetwork "%s" to handler named "%s"'
            % (predebug, network, handler.name)
        )


def attach_custom_field(object, custom_field_name):
    try:
        field = CustomField.objects.get(name=custom_field_name)
        object.custom_fields.add(field)
        object.save()
        if debug:
            print(
                '{}Attached CustomField "{}" to object "{}"'.format(
                    predebug, field, object
                )
            )
    except CustomField.DoesNotExist:
        if debug:
            print(
                '{}Could not find CustomField named "{}" to attach to object "{}"'.format(
                    predebug, custom_field_name, object
                )
            )


def attach_preconfiguration(object, preconfiguration):
    object.preconfigurations.add(preconfiguration)
    object.save()
    if debug:
        print(
            '%sAttached preconfiguration "%s" to object named "%s"'
            % (predebug, preconfiguration, object.name)
        )


def attach_preconfiguration_option(object, pcvs):
    object.preconfiguration_options.add(pcvs)
    object.save()
    if debug:
        print(
            '%sAttached preconfiguration valueset "%s" as option to object named "%s"'
            % (predebug, pcvs, object.name)
        )


def attach_custom_field_value(field_name, value, object):
    cf = CustomField.objects.get(name=field_name)
    cfv, created = CustomFieldValue.objects.get_or_create(field=cf, value=value)
    object.custom_field_values.add(cfv)
    object.save()
    if debug:
        print(
            '%sAttached CustomFieldValue "%s" to object named "%s"'
            % (predebug, cfv, object)
        )


def attach_custom_field_option(object, custom_field_option):
    object.custom_field_options.add(custom_field_option)
    object.save()
    if debug:
        print(
            '%sAttached CustomFieldValue "%s" as option to object named "%s"'
            % (predebug, custom_field_option, object.name)
        )


def attach_osbuild_attributes_to_object(object, os_build_attributes):
    if not isinstance(os_build_attributes, object.os_build_attributes.model):
        # Calling add() below would also raise a TypeError, but it would break
        # any ongoing transactions, so we manually raise the error.
        raise TypeError(
            "Cannot add {} to {}".format(
                os_build_attributes.__class__.__name__, object.__class__.__name__
            )
        )
    object.os_build_attributes.add(os_build_attributes)
    if debug:
        print(
            '%sAttached OSBuildAttribute "%s" to object named "%s"'
            % (predebug, os_build_attributes, object.name)
        )


def create_provision_order(
    user=None,
    project=None,
    environment=None,
    os_build=None,
    hostname=None,
    custom_field_values={},
    preconfig_values={},
    apps=[],
    quantity=1,
):

    # user, project, environment, and os_build are all strings that match
    # the name of a given CloudBolt object
    # custom_field_values and preconfig_values are python dictionaries
    # in the format of name: value
    # hostname is optional, can be skipped to either rely on default
    # naming convention or rely on resource pool

    missing_inputs = []
    if not user:
        missing_inputs.append("user")

    if not project:
        missing_inputs.append("project")

    if not environment:
        missing_inputs.append("environment")

    if not os_build:
        missing_inputs.append("os_build")

    if missing_inputs:
        print(
            "Error! You must supply the following arguments: %s"
            % (", ".join(missing_inputs))
        )
        return [0, None]

    if not custom_field_values and not preconfig_values:
        print(
            "Error! You must supply a python dictionary for either custom_field_values or preconfig_values!"
        )
        return [0, None]

    user_objects = User.objects.filter(username=user)
    if user_objects:
        user_object = user_objects[0]
        profile_object = user_object.userprofile
    else:
        print("Error! No user found for %s" % (user))
        return [0, None]

    project_objects = Group.objects.filter(name=project)
    if project_objects:
        project_object = project_objects[0]
    else:
        print("Error! No project found for %s" % (project))
        return [0, None]

    environment_objects = Environment.objects.filter(name=environment)
    if environment_objects:
        environment_object = environment_objects[0]
    else:
        print("Error! No environment found for %s" % (environment))
        return [0, None]

    os_build_objects = OSBuild.objects.filter(name=os_build)
    if os_build_objects:
        os_build_object = os_build_objects[0]
    else:
        print("Error! No OSBuild found for %s" % (os_build))
        return [0, None]

    cf_value_objects = []
    if custom_field_values:
        for cf_name, cf_value in list(custom_field_values.items()):
            cf_field_object, obj_created = CustomField.objects.get_or_create(
                name=cf_name
            )
            if cf_field_object.type == "NET":
                # for network type CFs, we have to look up the network object by
                # name and set the CFV.value to the network object itself
                network = ResourceNetwork.objects.get(name=cf_value)
                network = network.cast()
                cf_value_object, obj_created = CustomFieldValue.objects.get_or_create(
                    field=cf_field_object, value=network
                )
            else:
                # for all other types, just get or create it by its string val
                cf_value_object, obj_created = CustomFieldValue.objects.get_or_create(
                    field=cf_field_object, value=cf_value
                )
            cf_value_objects.append(cf_value_object)

    order_object = Order(owner=profile_object, group=project_object)
    order_object.save()

    pc_value_objects = []
    if preconfig_values:
        for pc_name, pc_value in list(preconfig_values.items()):
            pc_object, obj_created = Preconfiguration.objects.get_or_create(
                name=pc_name
            )
            (
                pc_value_object,
                obj_created,
            ) = PreconfigurationValueSet.objects.get_or_create(
                preconfiguration=pc_object, value=pc_value
            )
            pc_value_objects.append(pc_value_object)

    app_value_objects = []
    if apps:
        for app_name in apps:
            app_object, obj_created = Application.objects.get_or_create(name=app_name)
            app_value_objects.append(app_object)

    if environment_object.resource_pool:
        # ignore hostname, since this environment uses a resource pool
        order_item = ProvisionServerOrderItem(
            order=order_object,
            environment=environment_object,
            os_build=os_build_object,
            quantity=quantity,
        )
        order_item.save()
    else:
        # no resource pool, set up a basic hostname if none provided
        if not hostname:
            hostname = "autoprov-%s" % (int(time.time()))

        order_item = ProvisionServerOrderItem(
            order=order_object,
            environment=environment_object,
            os_build=os_build_object,
            hostname=hostname,
            quantity=quantity,
        )
        order_item.save()

    if debug:
        print(
            "%sAdded order item '%s' to order '%s'"
            % (predebug, order_item, order_object)
        )

    # associate applications with this order item
    if app_value_objects:
        order_item.applications.set(app_value_objects)

    # associate preconfiguration values with this order item
    if pc_value_objects:
        order_item.preconfiguration_values.set(pc_value_objects)

    # associate custom field values with this order item
    if cf_value_objects:
        order_item.custom_field_values.set(cf_value_objects)

    order_object.submit()

    if debug:
        print(
            "%sSubmitted order '%s' (id: %s)"
            % (predebug, order_object, order_object.id)
        )

    return [1, order_object]


def wait_for_job(job, timeout_secs=60 * 60):
    t1 = time.time()
    timeout_time = t1 + timeout_secs
    job = Job.objects.get(pk=job.id)
    while job.is_active():
        time.sleep(5)
        job = Job.objects.get(pk=job.id)
        if time.time() > timeout_time:
            raise TimeoutException(
                "Job {} timed out after {}s with status {}.".format(
                    job.id, timeout_secs, job.status
                )
            )
    print("Job's done!  ID: {}, status: {}".format(job.id, job.status))
    return


def wait_for_jobs(jobs):
    for job in jobs:
        wait_for_job(job)


def approve_order_and_start(order_id):
    order_object = Order.objects.get(pk=order_id)
    if order_object.status == "PENDING":
        job_objects = order_object.approve()[0]
    else:
        # must have been auto-approved
        job_objects = []
        order_items = order_object.orderitem_set.all()
        for order_item in order_items:
            job_objects += order_item.job_set.all()

    # print the URL to each of the jobs
    for job in job_objects:
        print(job.get_full_url())

    return job_objects


def create_decom_order(server_objects):
    # filter out servers that don't match the group on the first server
    server_objects = [x for x in server_objects if x.group == server_objects[0].group]

    order_object = Order(owner=server_objects[0].owner, group=server_objects[0].group)
    order_object.save()

    for server in server_objects:
        order_item = DecomServerOrderItem(
            order=order_object, environment=server.environment, pre_decom=False
        )
        order_item.save()
        order_item.servers.add(server)
        order_item.save()

    if debug:
        print(
            "%sAdded order item '%s' to order '%s'"
            % (predebug, order_item, order_object)
        )

    order_object.submit()

    if debug:
        print(
            "%sSubmitted order '%s' (id: %s)"
            % (predebug, order_object, order_object.id)
        )

    return [1, order_object]


def create_hook_point(name, label, description="", job_type=None):
    """
    Create a new HookPoint with the name, label, and description property
    values. If a HookPoint of the given name already exists, its label and
    description fields will be updated.
    """
    # FIXME currently the job_type is ignored

    hook_point, created = HookPoint.objects.get_or_create(name=name)
    # we allow revisions of our object files to change the label and
    # description willy-nilly
    hook_point.label = label
    hook_point.description = description
    hook_point.job_type = job_type
    hook_point.save()


def create_hook(
    name,
    hook_point,
    module,
    description=None,
    enabled=False,
    shared=False,
    custom_fields=None,
    skip_hook_point=False,
    hook_point_attributes={},
    run_on_statuses="",
    inputs=None,
    resource_technologies=None,
    os_families=None,
    **kwargs,
):
    """
    This method will create a new hook if one of this name does not already
    exist.  If one does already exist, this method will update it as appropriate with the
    module, type, description and enabled settings being passed from the caller.
    Also updates all hooks to indicate they are OOTB.

    hook_point_attributes is a dictionary containing additional values (like the button label) to
    set on the HookPointAction object (or ResourceAction in the case of resource actions)

    `run_on_statuses`: optional string of job status this action should be run
    on (only available to Post-* orchestration actions).
    """
    custom_fields = custom_fields if custom_fields else []
    inputs = inputs if inputs else []
    resource_technologies = resource_technologies if resource_technologies else []
    os_families = os_families if os_families else []
    filepath = os.path.join(cloudbolt_rootdir, module)

    if not hook_point:
        skip_hook_point = True

    extras = {}
    if "hook_type" in kwargs:
        if kwargs.get("hook_type") == "remote_script":
            model = RemoteScriptHook
        elif kwargs.get("hook_type") == "ipam_hook":
            model = IPAMHook
            extras["ipam_technology"] = IPAMTechnology.objects.get(
                name=kwargs["ipam_technology"]
            )
        elif kwargs.get("hook_type") == "dataprotection_hook":
            model = DataProtectionHook
            extras["dataprotection_technology"] = DataProtectionTechnology.objects.get(
                name=kwargs["dataprotection_technology"]
            )
        elif kwargs.get("hook_type") == "itsm_hook":
            model = ITSMHook
            extras["itsm_technology"] = ITSMTechnology.objects.get(
                name=kwargs["itsm_technology"]
            )
            extras["action"] = kwargs.get("action")
        elif kwargs.get("hook_type") == "servicenow_hook":
            model = ServiceNowHook
            extras["action"] = kwargs.get("action")
    else:
        model = CloudBoltHook

    hook, created = model.objects.get_or_create(
        name=name,
        defaults={
            "shared": shared,
            "module_file": filepath,
            "ootb_module_file": filepath,
            **extras,
        },
    )

    # If the file has not been modified from its OOTB state, update it to the
    # new version. Otherwise do nothing: we don't want to overwrite user edits.
    if hook.ootb_module_file == hook.module_file:
        setattr(hook, "module_file", filepath)
    # Update the OOTB file to the new version
    setattr(hook, "ootb_module_file", filepath)

    # All actions created here are OOTB
    hook.is_ootb = True
    hook.description = description
    hook.save()

    for input_conf in inputs:
        update_or_create_hook_input(hook, **input_conf)

    for cf_name in custom_fields:
        if cf_name.endswith("*"):
            # This may be an action input that ends with '_aNNN', we will search for any that
            # match and associate them with this hook. This is the case for Scale Resource's
            # 'service_item' action input, created earlier in the run of create_objects.
            cfs = CustomField.objects.filter(name__startswith=cf_name[:-1])
            cf_names = cfs.values_list("name", flat=True)
            for cf_name in cf_names:
                attach_custom_field(hook, cf_name)
        else:
            attach_custom_field(hook, cf_name)

    for technology_name in resource_technologies:
        resource_technology = ResourceTechnology.objects.get(name=technology_name)
        hook.resource_technologies.add(resource_technology)

    if hasattr(hook, "os_families"):
        for family_name in os_families:
            os_family = OSFamily.objects.get(name=family_name)
            hook.os_families.add(os_family)

    if not skip_hook_point:
        hook_point_obj = HookPoint.objects.get(name=hook_point)

        if hook_point == "resource_actions":
            # It's a resource hook, so create a ResourceAction, rather than a HookPointAction
            cls = ResourceAction
            search_kwargs = {"label": hook_point_attributes.get("label", "")}
        elif hook_point == "server_actions":
            cls = ServerAction
            search_kwargs = {"label": hook_point_attributes.get("label", "")}
        elif hook_point == "ipam_hook":
            cls = IPAMHook
            search_kwargs = {"label": hook_point_attributes.get("label", "")}
        else:
            # all other hook points will get a HookPointAction (they appear in the usual
            # Orchestration Actions UI)
            cls = HookPointAction
            search_kwargs = {"hook_point": hook_point_obj, "name": name}
            # TODO: move the HPA-specific data to hook_point_attributes like it is for
            # ResourceActions
            hook_point_attributes = search_kwargs.copy()

            if run_on_statuses:
                hook_point_attributes["run_on_statuses"] = run_on_statuses

        # any ServerAction, ResourceAction or HookPointAction supports enabled attribute
        hook_point_attributes["enabled"] = enabled

        # Make sure at least one HookPointAction exists for this hook & hook_point
        # with this name. If so, reload certain parameters. If not, create it.
        hook_point_actions = cls.objects.filter(hook=hook, **search_kwargs)
        if not hook_point_actions.exists():
            # if creating this hook with a run_seq, increment the run_seq of
            # all hooks that should come after it
            run_seq = hook_point_attributes.get("run_seq")
            if run_seq:
                hook_point_obj.hookpointaction_set.filter(run_seq__gte=run_seq).update(
                    run_seq=F("run_seq") + 1
                )
            # only change the enabled flag & desc if this is a newly created hook:
            # point action (if the customer has changed this stuff, leave it alone)
            hook_point_actions = [
                cls.objects.create(hook=hook, **hook_point_attributes)
            ]

        else:
            # Reload extra_classes for built-in actions.
            extra_classes = hook_point_attributes.get("extra_classes", None)
            if extra_classes:
                for hpa in hook_point_actions:
                    if hasattr(hpa, "extra_classes"):
                        # If the customer has overridden extra_classes, leave it alone.
                        if not hpa.extra_classes:
                            hpa.extra_classes = extra_classes
                            hpa.save()

        # These are a different set of mappings than the ones handled in
        # create_rule; at different levels of the dictionary
        if "mappings" in kwargs:
            mappings = kwargs.get("mappings")
            for key, value in list(mappings.items()):
                mapping = get_or_create_hook_input_mapping(
                    hook,
                    create_custom_field_value("{}_a{}".format(key, hook.id), value),
                )
                for hpa in hook_point_actions:
                    hpa.input_mappings.add(mapping)

    return hook


def get_or_create_hook_input_mapping(hook, default_value):
    """
    Get or create a RunHookInputMapping for the hook input, setting its
    default value to the one provided only when creating (we don't want to
    change it on an existing RunHookInputMapping in case a customer has set it
    to something different)
    """
    hi = hook.input_fields.filter(name=default_value.field.name).first()
    # There may be more than one here, so a get_or_create would except
    input_mapping = RunHookInputMapping.objects.filter(hook_input=hi).first()
    if not input_mapping:
        input_mapping = RunHookInputMapping.objects.create(
            hook_input=hi, default_value=default_value
        )

    return input_mapping


def get_or_create_namespace(name):
    namespace, _ = Namespace.objects.get_or_create(name=name)
    return namespace


def update_or_create_hook_input(
    hook,
    name=None,
    label=None,
    description=None,
    type=None,
    value_pattern_string=None,
    minimum=None,
    maximum=None,
    placeholder=None,
    required=True,
    namespace=None,
    regex_constraint=None,
    hide_if_default_value=False,
    relevant_osfamilies=[],
    global_options=[],
    allow_multiple=False,
    **kwargs,
):

    input_name = "{}_a{}".format(name, hook.id)
    hi = hook.input_fields.filter(name=input_name).first()

    if not hi:
        hi = HookInput.objects.create(
            hook=hook,
            name=input_name,
            required=required,
            label=label,
            type="STR",
            hide_if_default_value=hide_if_default_value,
            allow_multiple=allow_multiple,
        )
        if global_options:
            create_custom_field_global_options(input_name, global_options)

    for osf_dict in relevant_osfamilies:
        osf_dict.pop("pk", None)
        osf, _ = OSFamily.objects.get_or_create(**osf_dict)
        osf.dependent_fields.add(hi)
        osf.save()

    if label:
        # only update label if one is passed to this method
        hi.label = label

    if not type:
        # default hook_input type is STR
        type = "STR"

    if namespace:
        hi.namespace = get_or_create_namespace(namespace)

    hi.description = description
    hi.placeholder = placeholder
    hi.type = type
    hi.value_pattern_string = value_pattern_string
    hi.required = required

    hi.save()

    if minimum or maximum or regex_constraint:
        cfm = CustomFieldMapping.global_constraints.filter(custom_field=hi).first()
        if not cfm:
            cfm = CustomFieldMapping.global_constraints.create(custom_field=hi)

        # Do not override a min or max already set by the users. Whether the values on CFM are
        # "" or None, it's considered unset.
        if minimum and not cfm.minimum:
            cfm.minimum = minimum
        if maximum and not cfm.maximum:
            cfm.maximum = maximum
        if regex_constraint and not cfm.regex_constraint:
            cfm.regex_constraint = regex_constraint
        cfm.save()

    return hi


def create_rule(
    name,
    condition,
    action,
    description=None,
    enabled=False,
    shared=False,
    label=None,
    mappings={},
):
    """
    This method will create a new rule if one of this name does not
    already exist. If one does already exist, this method will update it with
    the description and enabled settings before being passed from the caller.

    Note that Action Inputs will appear on the form in the order that they are
    defined on the "action". For an example, see the rule named
    "scan_for_physical_servers" in cb_minimal.py
    """
    condition["hook_point"] = name
    condition["skip_hook_point"] = True
    _condition = create_hook(**condition)

    input_order = []
    for input_conf in condition.get("inputs", []):
        # need to make sure the hook inputs are the correct type and all because
        # we might need to create CFV values for this in rules mapping below
        hi = update_or_create_hook_input(_condition, **input_conf)
        input_order.append(hi.id)
    _condition.sequence_action_inputs(input_order)

    # avoided use of get_or_create due to issues with child object ids not being
    # set propertly when instantiating a parent object first.
    _rule = TriggerPoint.objects.filter(name=name)
    if len(_rule) > 0:
        _rule = _rule[0]
    else:
        _rule = TriggerPoint()
        _rule.name = name
        # Don't override enabled vs disabled on existing rule
        _rule.enabled = enabled
    _rule.label = label
    _rule.description = description
    _rule.condition = _condition
    _rule.save()

    for key, value in list(mappings.items()):
        _rule.condition_input_mappings.add(
            get_or_create_hook_input_mapping(
                _condition,
                create_custom_field_value("{}_a{}".format(key, _condition.id), value),
            )
        )

    action["hook_point"] = name
    create_hook(**action)


def update_or_create_load_balancer_technology(lb_tech_dict):
    """
    Create a load balancer tech based on dict values
    """
    # the lb_tech_dict looks like this:
    # {
    #    'name': 'Some Name',
    #    'type_slug': ["f5", "haproxy", "nsx_esg", "aws_elb", "azure_alb"]
    #    'version': 'X.X'
    #    'icon_image': "some/path/to/image"
    #    'actions': {
    #        'construct': "some/path/to/action"
    #        'destroy': "some/path/to/action"
    #        'add': "some/path/to/action"
    #        'remove': "some/path/to/action"
    #    }
    # }
    lb_tech = LoadBalancerTechnology.objects.filter(
        type_slug=lb_tech_dict["type_slug"], version=lb_tech_dict.get("version", None)
    ).first()

    if not lb_tech:
        # create new
        lb_tech = LoadBalancerTechnology(
            name=lb_tech_dict["name"],
            type_slug=lb_tech_dict["type_slug"],
            version=lb_tech_dict.get("version", None),
        )
    if "icon_image" in lb_tech_dict:
        icon_path = lb_tech_dict["icon_image"]
        icon_name = os.path.basename(icon_path)
        lb_tech.icon_image.save(icon_name, File(open(icon_path)))
    lb_tech.save()

    return lb_tech


def create_blueprint(bpdict):
    """
    Makes use of the ServiceBlueprintSerializer's create_resource_from_metadata
    to create a Blueprint based on the dictionary passed in.
    Currently can only set the attributes of a BP that are defined in the
    metadata dictionary, not the additional pieces that may have been exported
    in a zip file, such as action blueprint items or resource actions.
    To create the dictionary, export a BP and copy the JSON from the
    <bp_name>.json file.
    """
    # TODO: allow actually editing existing BPs and/or make the handling of
    # existing BPs better. Would kind of like to say "Also, if a BP with the
    # given name already exists, it will be replaced." in the docstring above.
    bps_with_name = ServiceBlueprint.objects.filter(name=bpdict["name"])
    if bps_with_name.exists():
        return bps_with_name.first()
    else:
        from servicecatalog.serializers import ServiceBlueprintSerializer

        bps = ServiceBlueprintSerializer()
        bps.replace_existing = True
        temp_files = {}
        icon = bpdict.get("icon")
        if icon:
            # Need to copy the file to a temporary spot, otherwise it'll be removed
            # from the initialize dir and cause issues the next time create_objects
            # is run
            filename = os.path.basename(icon)
            # use full path for icon
            icon_path = os.path.join(settings.ROOTDIR, icon)
            temp_dir = mkdtemp(prefix="tmp-iemixin-")
            temp_path = os.path.join(temp_dir, filename)
            shutil.copy(icon_path, temp_path)
            temp_files[icon] = temp_path
        bp = bps.create_resource_from_metadata(bpdict, temp_files=temp_files)
        return bp


def create_portal(name, **kwargs):
    """
    This method will create a new PortalConfig if one of this name does not
    already exist. It does not make changes to existing PortalConfigs, so that
    customer changes remain intact
    """
    # We use this approach instead of get_or_create in case there are
    # multiple Portals with the given name
    exists = PortalConfig.objects.filter(name=name).exists()
    if not exists:
        PortalConfig.objects.create(name=name, **kwargs)


def create_static_page(name, **kwargs):
    StaticPage.objects.update_or_create(name=name, defaults=kwargs)


def create_dataprotection_technology(name, **kwargs):
    """
    This method will create a new DataProtectionTechnology if one of this name does not
    already exist. If one does exist, it will update the record with the supplied data.
    """
    DataProtectionTechnology.objects.update_or_create(name=name, defaults=kwargs)
