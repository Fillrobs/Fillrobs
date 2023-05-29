#!/usr/bin/env python
from __future__ import unicode_literals, print_function
import getpass
from importlib.machinery import SourceFileLoader
import os
import pwd
import shutil
import sys

from django.conf import settings

os.environ["DJANGO_SETTINGS_MODULE"] = "settings"

create_objects_dir = os.path.dirname(__file__)
cloudbolt_rootdir = os.path.abspath(create_objects_dir)
cloudbolt_parentdir = os.path.dirname(cloudbolt_rootdir)
sys.path.insert(0, cloudbolt_parentdir)

if __name__ == "__main__":
    import django

    django.setup()

import c2_wrapper as c2
from accounts.models import GroupType, CBPermission
from behavior_mapping.models import ResourcePoolMapping
from cbhooks.models import OrchestrationHook, HookMapping, RecurringActionJob
from costs.models import ApplicationRate, CustomFieldRate, OSBuildRate
from containerorchestrators.models import ContainerOrchestratorTechnology
from cscv.models import CITConf
from externalcontent.models import Application, OSBuild, OSFamily
from infrastructure.models import (
    CustomField,
    DataCenter,
    Environment,
    ResourcePool,
    ResourcePoolValueSet,
)
from jobs.models import RecurringJob, HookParameters
from orders.models import CustomFieldValue
from product_license.enums.product_type import ProductTypeEnum
from product_license.methods import has_personality
from resourcehandlers.models import ResourceLimitItem
from resourcehandlers.slayer.models import SlayerResourceHandler
from resourcehandlers.vmware.models import VmwareDatastore
from tenants.models import TenantPermission, TenantRole
from utilities.logger import ThreadLogger

logger = ThreadLogger(__name__)


def create_pcvs(options_dict, preconfiguration, environment=None):
    pcv = c2.create_preconfiguration_value_set(
        value=options_dict["name"], preconfiguration=preconfiguration
    )
    if not pcv:
        # the PCVS already existed, do not change it
        return

    if environment:
        c2.attach_preconfiguration_option(object=environment, pcvs=pcv)

    os_build = options_dict.get("os_build", "")
    if os_build:
        pcv.os_build = OSBuild.objects.get(name=os_build)
        preconfiguration.include_os_build = True

    applications = options_dict.get("applications", [])
    if applications:
        for application in applications:
            pcv.applications.add(Application.objects.get(name=application))
        preconfiguration.include_applications = True

    pcv.save()
    preconfiguration.save()

    values = options_dict.get("values", {})
    for k, v in list(values.items()):
        c2.attach_custom_field(object=preconfiguration, custom_field_name=k)
        c2.attach_custom_field_value(field_name=k, value=v, object=pcv)


def attach_swpol_to_environment_and_pe(swpol, environment):
    application = Application.objects.get(name=swpol["name"])
    software_policy = application.vendorapplication_set.all()[0].cast()

    c2.attach_application_to_environment(
        application=application, environment=environment
    )

    c2.attach_software_policy_to_object(
        object=environment.provision_engine, software_policy=software_policy
    )
    if "osbuilds" in swpol:
        for os_dict in swpol["osbuilds"]:
            c2.attach_os_build_to_software_policy(
                os_build=os_dict["name"], software_policy=software_policy
            )


def attach_osbuild_to_environment_and_rh(osbuild, env):
    rh = env.resource_handler.cast()
    logger.debug("    Attaching OS Build '%s'" % osbuild["name"])
    osbuild = OSBuild.objects.get(name=osbuild["name"])
    c2.attach_osbuild_to_environment(osbuild, env)

    # First detach all OSBAs from the handler to avoid multiple OSBAs for a
    # build (an error condition) and to support our use of both labs' objects
    # for setting up demo and test instances until we've fully separated out
    # common data.
    for osba in rh.os_build_attributes.filter(os_build=osbuild):
        osba = osba.cast()
        logger.debug("      Removing OSBA '%s'" % osba)
        rh.os_build_attributes.remove(osba)

    for osba in osbuild.osbuildattribute_set.all():
        # The reason we try attaching an OSBA here is that many in this list
        # are for another resource technology so don't apply.
        try:
            c2.attach_osbuild_attributes_to_object(rh, osba.cast())
            logger.debug("      Added OSBA '%s'" % osba)
            # There should only be one OSBA for this OS Build and this tech, but
            # break anyway in case this cb_objects has more.
            break
        except TypeError:
            # It's for the wrong resource tech so skip it
            pass


def create_aws_build(build_dict):
    osbuild = c2.create_osbuild(name=build_dict["name"], template=True)
    c2.create_aws_osbuild_attributes(osbuild, build_dict)
    return osbuild


def create_openstack_build(build_dict):
    osbuild = c2.create_osbuild(name=build_dict["name"], template=True)
    c2.create_os_osbuild_attributes(os_build=osbuild, osi_id=build_dict["osi_id"])
    return osbuild


def create_vmtemplate_build(build_dict):
    osbuild = c2.create_osbuild(name=build_dict["name"], template=True)
    c2.create_vsphere_osbuild_attributes(
        os_build=osbuild,
        guest_id=build_dict["guest_id"],
        template_name=build_dict["vmware_template"],
    )
    return osbuild


def create_xentemplate_build(build_dict):
    osbuild = c2.create_osbuild(name=build_dict["name"], template=False)
    c2.create_xen_osbuild_attributes(
        os_build=osbuild, template_name=build_dict["xen_template"]
    )
    return osbuild


def create_slayertemplate_build(build_dict):
    osbuild = c2.create_osbuild(name=build_dict["name"], template=True)
    c2.create_slayer_osbuild_attributes(
        os_build=osbuild,
        template_name=build_dict["slayer_template"],
        uuid=build_dict["uuid"],
    )
    return osbuild


def create_qemutemplate_build(build_dict):
    osbuild = c2.create_osbuild(name=build_dict["name"], template=True)
    c2.create_qemu_osbuild_attributes(
        os_build=osbuild, template_name=build_dict["qemu_template"]
    )
    return osbuild


def create_data_center(dc_dict):
    """
    In this method, I'm intentionally diverging from the convention in
    this file of not interacting directly with the Django API.  In this case,
    KISS overrides the benefit of a layer of abstraction from Django.
    """
    DataCenter.objects.get_or_create(name=dc_dict["name"], address=dc_dict["address"])


def create_limits(resource_handler, limits):
    for cfname, max in list(limits.items()):
        field, created = CustomField.objects.get_or_create(name=cfname)
        limits = ResourceLimitItem.objects.filter(
            custom_field=field, handler=resource_handler
        )
        if not limits:
            limit = ResourceLimitItem.objects.create(
                custom_field=field, handler=resource_handler, maximum=max
            )
        else:
            limit = limits[0]
            if limit.maximum != max:
                limit.maximum = max
                limit.save()


def set_rates(cb_objects):
    logger.debug("Setting Global Rates")

    if hasattr(cb_objects, "global_cf_rates"):
        logger.debug("  Global CF rates")
        set_cf_rates(cb_objects.global_cf_rates)

    if hasattr(cb_objects, "global_app_rates"):
        logger.debug("  Global application rates")
        set_app_rates(cb_objects.global_app_rates)

    if hasattr(cb_objects, "global_os_rates"):
        logger.debug("  Global OS rates")
        set_os_rates(cb_objects.global_os_rates)

    set_pcvs_rates()


def set_env_rates(env, env_rates):
    if not env_rates:
        return
    logger.debug("Setting rates on env '%s'" % env)
    set_cf_rates(env_rates.get("cf_rates", {}), env)
    set_app_rates(env_rates.get("app_rates", {}), env)
    set_os_rates(env_rates.get("os_rates", {}), env)


def set_cf_rates(rates_dict, env=None):
    """
    Create or update global or env-specific CF rates
    """
    for cf_name, rate in list(rates_dict.items()):
        cf, created = CustomField.objects.get_or_create(name=cf_name)
        cfr, created = CustomFieldRate.objects.get_or_create(
            custom_field=cf, environment=env
        )
        if cfr.rate != rate:
            cfr.rate = rate
            cfr.save()


def set_app_rates(rates_dict, env=None):
    """
    Create or update global or env-specific app rates
    """
    for app_name, rate in list(rates_dict.items()):
        (app, created) = Application.objects.get_or_create(name=app_name)
        (app_rate, created) = ApplicationRate.objects.get_or_create(
            application=app, environment=env
        )
        if app_rate.rate != rate:
            app_rate.rate = rate
            app_rate.save()


def set_os_rates(rates_dict, env=None):
    """
    Create or update global or env-specific OS build rates
    """
    for os_name, rate in list(rates_dict.items()):
        (os, created) = OSBuild.objects.get_or_create(name=os_name)
        (os_rate, created) = OSBuildRate.objects.get_or_create(
            os_build=os, environment=env
        )
        if os_rate.rate != rate:
            os_rate.rate = rate
            os_rate.save()


def set_pcvs_rates():
    """
    This one isn't defined yet.
    """
    return


def create_global_resource_pool(rp_dict):
    """
    This logic differed significantly enough from the per-environment RP creation
    logic in create_objects.py and c2_wrapper.py that it warranted its own
    method.  This method does not deal with hostnames, IPs, etc, only CFVs in
    the pool
    """
    name = rp_dict.get("name", "")
    if not name:
        raise Exception("Global Resource Pools must have a name defined.")
    logger.debug("  {}".format(name))
    rp, created = ResourcePool.objects.get_or_create(name=name, global_scope=True)

    for cfv_dict in rp_dict["cfvs"]:
        cfvs = []
        # longest-running step in create_objects, so show some progress
        sys.stdout.write(".")
        sys.stdout.flush()
        for cf_name, cf_value in list(cfv_dict.items()):
            cf, created = CustomField.objects.get_or_create(name=cf_name)
            cfv, created = CustomFieldValue.objects.get_or_create(
                field=cf, value=cf_value
            )
            cfvs.append(cfv)
            if cf not in rp.custom_fields.all():
                rp.custom_fields.add(cf)
                rp.save()
        rpvs = ResourcePoolValueSet.objects.create(resource_pool=rp)
        rpvs.custom_field_values.set(cfvs)
        rpvs.save()
    logger.debug(".")


def get_or_create_pool_for_network(pool_dict, network_object):
    if network_object.resourcepoolmapping_set.all():
        # only create the resource pool for this network if a mapping
        # doesn't already exist
        return
    rp = c2.create_resource_pool(pool_dict)
    ResourcePoolMapping.objects.create(pool=rp, network=network_object)


def create_vmware_networks(networks):
    network_objects = []
    for network in networks:
        if "netmask" not in network:
            network["netmask"] = None
        if "gateway" not in network:
            network["gateway"] = None
        if "addressing_schema" not in network:
            network["addressing_schema"] = "dhcp"
        network_object = c2.create_vmware_network(
            name=network["name"],
            dvSwitch=network["dvswitch"],
            network=network["vicname"],
            vlan=network["vlan"],
            adapterType=network["nictype"],
            addressing_schema=network["addressing_schema"],
            gateway=network["gateway"],
            netmask=network["netmask"],
            dns1=network.get("dns1"),
            dns2=network.get("dns2"),
        )
        if "ping_test" in network:
            set_ping_test(network_object)
        if "pool" in network:
            get_or_create_pool_for_network(network["pool"], network_object)
        network_objects.append(network_object)
    return network_objects


def create_vmware_rh(environment_dict, resource_technology):
    dict_opts = {}
    dict_opts = environment_dict["resource_handler"].copy()
    for key in [
        "limits",
        "networks",
        "custom_fields",
        "resource_technology",
        "datastores",
    ]:
        if key in dict_opts:
            del dict_opts[key]

    resource_handler = c2.create_vsphere_resource_handler(
        dict_opts["name"], dict_opts["ip"], resource_technology, dict_opts
    )
    limits = environment_dict["resource_handler"].get("limits", {})
    create_limits(resource_handler, limits)
    return resource_handler


def _determine_build_type(build_dict):
    """
    Based on attributes, determine what type of a build this is supposed to be
    """

    type_attributes = {
        "aws": ["ami_id"],
        "os": ["osi_id"],
        "vmsphere": ["vmware_template"],
        "xen": ["xen_template"],
        "qemu": ["qemu_template"],
        "razor": ["profile_name"],
        "slayer": ["slayer_template"],
        "?": ["guestid"],  # FIXME
    }

    os_build_type = None
    for itype, attributes in list(type_attributes.items()):
        # Check which attributes for this type are present:
        present_attributes = [attr for attr in attributes if attr in build_dict]
        # print "build_dict:", build_dict
        # print "attributes:", attributes
        # print "present_attributes for", itype, present_attributes
        if not present_attributes:
            continue
        elif len(present_attributes) == len(attributes):
            if os_build_type:
                raise ValueError(
                    "Can not determine build type of: %s" % build_dict["name"]
                )
            os_build_type = itype
        else:
            raise ValueError("Can not determine build type of: %s" % build_dict["name"])

    if not os_build_type:
        raise ValueError("Can not determine build type of: %s" % build_dict["name"])

    return os_build_type


def create_osbuild_generic(build_dict, skip=[]):
    build_type = _determine_build_type(build_dict)

    # RH builds
    if build_type == "aws":
        os_build = create_aws_build(build_dict)

    elif build_type == "os":  # openstack
        os_build = create_openstack_build(build_dict)

    elif build_type == "vmsphere":
        os_build = create_vmtemplate_build(build_dict)

    elif build_type == "xen":
        os_build = create_xentemplate_build(build_dict)

    elif build_type == "qemu":
        os_build = create_qemutemplate_build(build_dict)

    # PE builds
    elif build_type == "razor":
        os_build = c2.create_osbuild(name=build_dict["name"], template=False)
        c2.create_razor_profile(os_build, build_dict["profile_name"])

    elif build_type == "slayer":
        os_build = create_slayertemplate_build(build_dict)

    else:
        raise ValueError("Invalid build type for: %s" % build_dict["name"])

    if "os_family" in build_dict:
        os_build.os_family = OSFamily.objects.get(name=build_dict["os_family"])

    os_build.save()


def set_ping_test(network_object):
    hook = OrchestrationHook.objects.get(name="Ping Test")
    mapping, created = HookMapping.objects.get_or_create(
        hook=hook, network=network_object
    )
    mapping.should_execute = True
    mapping.save()


# create_{stepname} functions


def create_features(features, skip=[]):
    """
    Reads settings from customer and main settings files.

    Does not remove unlisted settings,
        this can be done by passing `clean=True` to `reload_features()`
    """
    if features["use_features"] is True:
        logger.debug("Setting feature switches")
        from features.methods import reload_features

        reload_features()


def create_gp(gp, skip=[]):
    smtp_host = gp.get("smtp_host", None)
    smtp_port = gp.get("smtp_port", 25)
    smtp_user = gp.get("smtp_user", "")
    smtp_password = gp.get("smtp_password", "")
    smtp_use_tls = gp.get("smtp_use_tls", False)
    if smtp_host:
        logger.debug("Setting SMTP Configuration")
        c2.set_smtp_prefs(smtp_host, smtp_port, smtp_use_tls, smtp_user, smtp_password)
    gp_obj = c2.create_global_preferences()
    cbadmin_email = gp.get("cbadmin_email", "")
    if cbadmin_email:
        gp_obj.cbadmin_email = gp.get("cbadmin_email", "")

    gp_obj.save()


def create_all_cfs(all_cfs, skip=[]):
    for field_dict in all_cfs:
        c2.create_custom_field(**field_dict)


def create_all_cfvs(all_cfvs, skip=[]):
    for field_name, options in list(all_cfvs.items()):
        c2.create_custom_field_options(field_name, options)


def create_all_cfos(all_cfos, skip=[]):
    for field_name, options in list(all_cfos.items()):
        c2.create_custom_field_global_options(field_name, options)


def create_data_centers(dcs=[], skip=[]):
    for dc_dict in dcs:
        create_data_center(dc_dict)


def create_all_vsphere_networks(all_vsphere_networks, skip=[]):
    for network in all_vsphere_networks:
        if "netmask" not in network:
            network["netmask"] = None
        if "gateway" not in network:
            network["gateway"] = None
        if "addressing_schema" not in network:
            network["addressing_schema"] = "dhcp"
        c2.create_vmware_network(
            name=network["name"],
            dvSwitch=network["dvswitch"],
            network=network["vicname"],
            vlan=network["vlan"],
            adapterType=network["nictype"],
            addressing_schema=network["addressing_schema"],
            gateway=network["gateway"],
            netmask=network["netmask"],
            dns1=network.get("dns1"),
            dns2=network.get("dns2"),
        )


def create_all_load_balancer_technologies(all_load_balancer_technologies, skip=None):
    for lbt_dict in all_load_balancer_technologies:
        c2.update_or_create_load_balancer_technology(lbt_dict)


def create_all_resource_technologies(all_resource_technologies, skip=[]):
    for field_dict in all_resource_technologies:
        c2.create_resource_technology(
            field_dict["name"],
            field_dict["version"],
            field_dict["module"],
            field_dict.get("slug", ""),
        )


def create_all_prov_technologies(all_prov_technologies, skip=[]):
    for field_dict in all_prov_technologies:
        c2.create_provision_technology(field_dict["name"], field_dict["version"])


def create_all_orchestration_technologies(all_orchestration_technologies, skip=[]):
    for tech_dict in all_orchestration_technologies:
        c2.create_orchestration_technology(**tech_dict)


def create_all_container_technologies(all_container_technologies, skip={}):
    for container_tech in all_container_technologies:
        count = ContainerOrchestratorTechnology.objects.filter(
            name=container_tech["name"]
        ).count()
        if count > 1:
            # clean up after a bug we used to have that created extras
            # can remove this block after 5.2
            empty_cos = ContainerOrchestratorTechnology.objects.filter(
                name=container_tech["name"], containerorchestrator=None
            )
            empty_cos.delete()
        ContainerOrchestratorTechnology.objects.get_or_create(
            name=container_tech["name"]
        )


def create_all_ipam_technologies(all_ipam_technologies, skip={}):
    for ipam_tech_dict in all_ipam_technologies:
        c2.create_ipam_technology(**ipam_tech_dict)


def create_all_itsm_technologies(all_itsm_technologies, skip={}):
    for itsm_tech_dict in all_itsm_technologies:
        c2.create_itsm_technology(**itsm_tech_dict)


def create_all_network_virtualization_technologies(
    all_network_virtualization_technologies, skip={}
):
    for nv_tech_dict in all_network_virtualization_technologies:
        c2.create_network_virtualization_technology(**nv_tech_dict)


def create_all_orchestration_engines(all_orchestration_engines, skip=[]):
    for field_dict in all_orchestration_engines:
        tech_dict = field_dict["technology"]
        ot = c2.create_orchestration_technology(**tech_dict)
        if ".hpoo." in tech_dict["modulename"]:
            c2.create_hpoo_engine(field_dict, ot)
        else:
            logger.debug(
                "Orchestration for Technology %s not supported, skipping" % (ot)
            )


def create_os_families(family_list, skip=[]):
    # creation of OSFamilies must happen before OSBuilds
    from django.core.files import File

    family_dict = {}
    for info in family_list:
        name = info["name"]
        parent = info.get("parent")

        family, _ = OSFamily.objects.get_or_create(name=name)
        family_dict[name] = family
        family.parent = family_dict.get(parent)

        for icon_type in ["inline_icon", "display_icon"]:
            if icon_type in info:
                icon_file = getattr(family, icon_type)
                if icon_file:
                    icon_file.delete()
                icon_path = os.path.join(c2.cloudbolt_rootdir, info[icon_type])
                icon_name = os.path.basename(icon_path)
                icon_file.save(icon_name, File(open(icon_path, "rb")))

        family.save()

    # The icons created above and their containing directory are ending up owned
    # by root instead of apache when this is run by the jobengine.
    # If/when the jobengine is run by a user other that root, this will need to
    # be updated. That user will also need permission to perform the chowns below.
    if not getpass.getuser() == "root":
        logger.debug("Skipping file ownership change for media root")
        return

    apache_user = pwd.getpwnam("apache")[2]
    apache_group = pwd.getpwnam("apache")[3]
    # Make sure everything in MEDIA_ROOT is owned by apache as well
    for dirpath, dirnames, filenames in os.walk(settings.MEDIA_ROOT):
        try:
            shutil.chown(dirpath, apache_user, apache_group)
            for filename in filenames:
                shutil.chown(os.path.join(dirpath, filename), apache_user, apache_group)
        except Exception:
            logger.debug(f"Error setting ownership of {settings.MEDIA_ROOT}")


def create_all_osbuilds(all_osbuilds, skip=[]):
    # creation of OSBuilds must happen after OSFamilies
    all_osbuild_names = set([osb["name"] for osb in all_osbuilds])

    # Delete any preexisting OSBAs to avoid conflicts when loading cb_objects
    # from more than one lab (until we've moved all common data out of the
    # rockville fixture, we need to load it first in reston, then reston's.
    for osb in OSBuild.objects.all():
        if osb.name in all_osbuild_names:
            osb.osbuildattribute_set.all().delete()

    for osbuild in all_osbuilds:
        create_osbuild_generic(osbuild, skip=skip)


def create_all_environments(all_environments, skip=[]):
    for environment_dict in all_environments:
        environment = None

        logger.debug("  Processing environment %s" % (environment_dict["name"]))

        if ("provision_engine" not in environment_dict) or (
            not environment_dict["provision_engine"]
        ):
            provision_engine = None
        else:
            if "provision_technology" not in environment_dict["provision_engine"]:
                logger.debug("provision_technology not defined for this environment, ")
                logger.debug(
                    "can not create! environment_dict: %s\n" % (environment_dict)
                )
                continue

            prov_eng_dict = environment_dict["provision_engine"]
            prov_tech_dict = prov_eng_dict["provision_technology"]
            provision_technology = c2.create_provision_technology(
                name=prov_tech_dict["name"], version=prov_tech_dict["version"]
            )

            provision_engine = c2.create_provision_engine(
                name=prov_eng_dict["name"],
                ip=prov_eng_dict["ip"],
                port=prov_eng_dict["port"],
                protocol=prov_eng_dict["protocol"],
                serviceaccount=prov_eng_dict["serviceaccount"],
                servicepasswd=prov_eng_dict["servicepasswd"],
                provision_technology=provision_technology,
            )

        if "resource_handler" in environment_dict:
            rh_dict = environment_dict["resource_handler"]
            rt_dict = rh_dict["resource_technology"]

            resource_technology = c2.create_resource_technology(
                rt_name=rt_dict["name"],
                rt_version=rt_dict["version"],
                rt_module=rt_dict["module"],
            )

            networks = []
            if "networks" in rh_dict:
                networks = rh_dict["networks"]

            network_objects = []

            # AWS RH
            if rt_dict["name"].startswith("Amazon"):
                dict_opts = rh_dict.copy()
                for key in [
                    "limits",
                    "networks",
                    "custom_fields",
                    "resource_technology",
                ]:
                    if key in dict_opts:
                        del dict_opts[key]
                resource_handler = c2.create_aws_handler(
                    dict_opts["name"], resource_technology, dict_opts
                )

                # For AWS, some CFs need to be attached directly to the
                # handler or things won't work, specifically aws_region
                for field_dict in rh_dict["custom_fields"]:
                    c2.attach_custom_field(
                        object=resource_handler, custom_field_name=field_dict["name"]
                    )

                if "aws_region_specific_envs" not in skip:
                    # In the case of AWS, let the RH create the environment, because
                    # it discovers all the region-specific info such as security groups,
                    # instance types, key pair names.
                    # Defaults to us-east-1 if no region is specified in the env dict
                    if (
                        Environment.objects.filter(
                            name=environment_dict["name"]
                        ).count()
                        == 0
                    ):
                        # This check ensures we don't try to re-create an Env with same name,
                        # in the case when create_objects is run on a populated DB.
                        environment = resource_handler.create_location_specific_env(
                            environment_dict.get("ec2_region", "us-east-1"),
                            environment_dict["name"],
                            environment_dict.get("vpc_id"),
                        )

            # OpenStack RH
            elif rt_dict["name"].startswith("OpenStack"):
                dict_opts = rh_dict.copy()
                for key in [
                    "limits",
                    "networks",
                    "custom_fields",
                    "resource_technology",
                ]:
                    if key in dict_opts:
                        del dict_opts[key]
                resource_handler = c2.create_openstack_handler(
                    dict_opts["name"], resource_technology, dict_opts
                )

            # QEMU-KVM RH
            elif rt_dict["name"].startswith("QEMU"):
                dict_opts = rh_dict.copy()
                for key in [
                    "limits",
                    "networks",
                    "custom_fields",
                    "resource_technology",
                ]:
                    if key in dict_opts:
                        del dict_opts[key]
                resource_handler = c2.create_qemu_resource_handler(
                    name=rh_dict["name"],
                    ip=rh_dict["ip"],
                    port=rh_dict["port"],
                    protocol=rh_dict["protocol"],
                    serviceaccount=rh_dict["serviceaccount"],
                    servicepasswd=rh_dict["servicepasswd"],
                    resource_technology=resource_technology,
                )

            # xen RH
            elif "default_sr" in rh_dict:
                for network in networks:
                    network_object = c2.create_xen_network(
                        name=network["name"],
                        network=network["network"],
                        vlan=network["vlan"],
                    )
                    network_objects.append(network_object)

                resource_handler = c2.create_xen_resource_handler(
                    name=rh_dict["name"],
                    ip=rh_dict["ip"],
                    port=rh_dict["port"],
                    protocol=rh_dict["protocol"],
                    serviceaccount=rh_dict["serviceaccount"],
                    servicepasswd=rh_dict["servicepasswd"],
                    resource_technology=resource_technology,
                    default_sr=rh_dict["default_sr"],
                )

                limits = rh_dict.get("limits", {})
                create_limits(resource_handler, limits)

            # vmware RH
            elif rh_dict["resource_technology"]["name"] == "VMware vCenter":
                network_objects = create_vmware_networks(networks)

                resource_handler = create_vmware_rh(
                    environment_dict, resource_technology
                )

                for network_object in network_objects:
                    c2.attach_network_to_handler(
                        network=network_object, handler=resource_handler
                    )

                datastores = environment_dict["resource_handler"].get("datastores", [])
                for datastore_dict in datastores:
                    VmwareDatastore.objects.get_or_create(
                        resource_handler=resource_handler, **datastore_dict
                    )

            # softlayer RH
            elif "IBM SoftLayer" in rh_dict["name"]:
                rh_dict.pop("networks")
                rhs = SlayerResourceHandler.objects.filter(
                    name=rh_dict["name"], resource_technology=resource_technology
                )
                if rhs:
                    resource_handler = rhs[0]
                else:
                    rh_dict.pop("resource_technology")
                    resource_handler = SlayerResourceHandler.objects.create(
                        resource_technology=resource_technology, **rh_dict
                    )
                for network in networks:
                    resource_handler.add_network(**network)

            else:
                raise ValueError(
                    "Can't determine type of resource handler: {0}".format(rh_dict)
                )

        else:
            resource_handler = None

        if not environment:
            environment = c2.create_environment(
                name=environment_dict["name"],
                resource_handler=resource_handler,
                provision_engine=provision_engine,
                data_center_name=environment_dict.get("data_center", None),
            )

        if (
            environment_dict.get("provision_engine")
            and "custom_fields" in environment_dict["provision_engine"]
        ):
            for field_dict in environment_dict["provision_engine"]["custom_fields"]:
                c2.attach_custom_field(
                    object=provision_engine, custom_field_name=field_dict["name"]
                )

        if environment_dict.get("provision_engine") and "custom_fields" in rh_dict:
            for field_dict in rh_dict["custom_fields"]:
                c2.attach_custom_field(
                    object=resource_handler, custom_field_name=field_dict["name"]
                )

        set_env_rates(environment, environment_dict.get("env_rates", {}))

        cfos = environment_dict.get("cfos")
        if cfos:
            for custom_field, values in list(cfos.items()):
                for value in values:
                    # For VMware datastores, get the datastore object (created
                    # above) by name before creating the CFV
                    if custom_field == "vmware_datastore":
                        value = VmwareDatastore.objects.get(
                            resource_handler=resource_handler, name=value
                        )
                    custom_field_value = c2.create_custom_field_value(
                        custom_field_name=custom_field, value=value
                    )
                    c2.attach_custom_field_option(
                        object=environment, custom_field_option=custom_field_value
                    )
                    c2.attach_custom_field(
                        object=environment, custom_field_name=custom_field
                    )

        if "osbuilds" in environment_dict:
            for osbuild in environment_dict["osbuilds"]:
                attach_osbuild_to_environment_and_rh(osbuild, environment)

        if "software_policies" in environment_dict:
            for swpol in environment_dict["software_policies"]:
                attach_swpol_to_environment_and_pe(swpol, environment)

        if "resource_pool" in environment_dict:
            if not environment.resource_pool:
                # only create the resource pool for this environment if one
                # doesn't already exist
                # otherwise we'll wind up creating a new resource pool
                # each time this script is run,
                # detaching from the old RP, and attaching to the new one
                resource_pool = c2.create_resource_pool(
                    environment_dict["resource_pool"]
                )
                c2.attach_resource_pool_to_environment(environment, resource_pool)

        if "preconfig_info" in environment_dict:
            for pc_dict in environment_dict["preconfig_info"]:
                preconfiguration = c2.create_preconfiguration(
                    name=pc_dict["name"], label=pc_dict["label"]
                )

                c2.attach_preconfiguration(
                    object=environment, preconfiguration=preconfiguration
                )

                if "options" in pc_dict:
                    for options_dict in pc_dict["options"]:
                        create_pcvs(options_dict, preconfiguration, environment)


def create_hook_points(hook_points, skip=[]):
    for hook_point in hook_points:
        c2.create_hook_point(**hook_point)


def create_hooks(hooks, skip=[]):
    for hook in hooks:
        c2.create_hook(**hook)


def create_rules(rules, skip=[]):
    for rule in rules:
        c2.create_rule(**rule)


def create_all_groups(all_groups, skip=[]):
    for group_dict in all_groups:
        logger.debug("  %s %s" % (group_dict["type"], group_dict["name"]))
        c2.create_cloudbolt_group(group_dict=group_dict)

    if c2.is_group_type_order_filter_defined():
        logger.debug(
            "The 'Valid group types for Orders' setting is already defined, not adding "
            "any group types"
        )
    else:
        logger.debug("Granting all group types the ability to request resources.")
        for group_type in GroupType.objects.all():
            c2.attach_group_type_to_gp(group_type)


def create_all_permissions(all_permissions, skip=[]):
    for permission_dict in all_permissions:
        CBPermission.objects.update_or_create(
            name=permission_dict["name"], defaults=permission_dict
        )


def create_all_special_roles(all_roles, skip=[]):
    for role_dict in all_roles:
        c2.create_role(role_dict)


def create_all_grouptype_roles(all_roles, skip=[]):
    for role_dict in all_roles:
        role_dict = role_dict.copy()
        group_type_names = role_dict.pop("group_types")
        role = c2.create_role(role_dict)
        for group_type_name in group_type_names:
            group_type = c2.create_group_type(group_type_name)
            role.group_types.add(group_type)


def create_all_superusers(all_superusers, skip=[]):
    for super_user_dict in all_superusers:
        logger.debug("  {}".format(super_user_dict["username"]))
        super_user = c2.create_cbadmin(
            username=super_user_dict["username"],
            first_name=super_user_dict["first_name"],
            last_name=super_user_dict["last_name"],
            password=super_user_dict["password"],
            email=super_user_dict["email"],
        )

        if "group_perms" in super_user_dict:
            for group_name, group_privs in list(super_user_dict["group_perms"].items()):
                logger.debug("    {}: {}".format(group_name, group_privs))
                c2.grant_cloudbolt_group_priv(group_name, group_privs, super_user)


def create_all_normalusers(all_normalusers, skip=[]):
    for normal_user_dict in all_normalusers:
        normal_user = c2.create_user(
            username=normal_user_dict["username"],
            first_name=normal_user_dict["first_name"],
            last_name=normal_user_dict["last_name"],
            password=normal_user_dict["password"],
            email=normal_user_dict["email"],
        )

        if "group_perms" in normal_user_dict:
            for group_name, group_privs in list(
                normal_user_dict["group_perms"].items()
            ):
                c2.grant_cloudbolt_group_priv(group_name, group_privs, normal_user)


def create_global_resource_pools(global_resource_pools, skip=[]):
    for grp in global_resource_pools:
        create_global_resource_pool(grp)


def create_jasper_reporting_engines(jasper_reporting_engines, skip=[]):
    for jasper_reporting_engine in jasper_reporting_engines:
        c2.create_jasperreport_engine(**jasper_reporting_engine)


def create_all_blueprints(all_blueprints, skip=[]):
    for blueprint in all_blueprints:
        logger.debug("  {}".format(blueprint["name"]))
        c2.create_blueprint(blueprint)


def create_portals(portals, skip=[]):
    for portal in portals:
        logger.debug("  {}".format(portal.get("name", "<no name>")))
        c2.create_portal(**portal)


def create_static_pages(static_pages, skip=[]):
    for page in static_pages:
        logger.debug("  {}".format(page.get("name", "<no name>")))
        c2.create_static_page(**page)


def create_all_preconfigs(preconfigs, skip=[]):
    for pc_dict in preconfigs:
        preconfiguration = c2.create_preconfiguration(
            name=pc_dict["name"], label=pc_dict["label"]
        )
        if not preconfiguration:
            # the preconfig already existed, do not change it
            return

        if "options" in pc_dict:
            for options_dict in pc_dict["options"]:
                create_pcvs(options_dict, preconfiguration)


def create_recurring_job(recurring_job_dict):
    """ Given a serialized recurring job dictionary, create a RecurringJob or RecurringActionJob.

    Handles these cases:
    1. If the recurring_job_dict is a RecurringActionJob:
        a. If a RecurringJob of this name exists, replace it with a RecurringActionJob.
           ^^^ Delete this logic after all customers are on 7.0.
        b. If a RecurringActionJob of this name exists, bail out.
        c. If a RecurringActionJob of this name doesn't exist, create one.
    2. If the recurring_job_dict is a RecurringJob:
        a. If a RecurringJob of this name exists, bail out.
        b. If a RecurringJob of this name doesn't exist, create one.

    recurring_job_dict comes in two flavors: one with a 'param_class' key that references the JobParameters type
    to create for this RecurringJob; or no 'param_class' key where 'type' == 'recurring_action', in which case
    a RecurringActionJob (which itself is RunHookMixin, hence has .hook/.run_hook_as_job) will be created.
        {
            'name': 'Execute all Rules',
            'description': 'Execute the condition for all active rules to ensure compliance in the '
                           'environment. See Admin > Rules for more info.',
            'type': 'runautomations',
            'param_class': TriggerParameters,
            'schedule': '0 1 * * *',
        },
        {
            'name': 'Refresh All Server Utilization',
            'enabled': False,
            'description': 'Execute any action whose name starts with "Refresh Utilization ".',
            'type': 'recurring_action',
            'hook_name': 'Refresh All Server Utilization',
            'schedule': '45 3 * * *',
        },

    Args:
        recurring_job_dict: the dictionary describingthe RecurringJob or RecurringActionJob (described in this docstr)

    Returns:
        None if it bailed out for some reason.
        an instance of RecurringJob (or a subclass) if it successfully created one

    """
    name = recurring_job_dict["name"]
    is_recurring_action_job = (
        "param_class" not in recurring_job_dict
        and recurring_job_dict["type"] == "recurring_action"
    )

    # Locate recurring job (or descendant) objects of the same name.
    existing_recurringjobs = RecurringJob.objects.filter(name=name)
    count_existing_recurringjobs = existing_recurringjobs.count()
    is_existing_recurring_action_job = False
    is_existing_recurring_job_with_action = (
        False  # Safe to delete when all customers are on >= 7.0
    )

    # Bail out if multiple recurring jobs of the same name exist.
    if count_existing_recurringjobs > 1:
        logger.debug(
            'Cannot create recurring job "{}" when multiple of the same name exist.'.format(
                name
            )
        )
        return
    existing_recurringjob = None

    # Bail out if object of correct type (of same name) already exists.
    if count_existing_recurringjobs == 1:
        bail_out = False
        existing_recurringjob = existing_recurringjobs.first()
        # existing_name = existing_recurringjob.name

        is_existing_recurring_action_job = hasattr(existing_recurringjob.cast(), "hook")

        # Safe to delete when all customers are on >= 7.0
        is_existing_recurring_job_with_action = (
            existing_recurringjob.type == "orchestration_hook"
            and isinstance(
                existing_recurringjob.parameters.cast()
                if existing_recurringjob.parameters
                else None,
                HookParameters,
            )
            and not is_existing_recurring_action_job
        )

        # Existing is Recurring Action Job (don't replace/update)
        if is_existing_recurring_action_job:
            bail_out = True
            # job_type = 'recurring action job'

        # Existing and New are Recurring Job (don't replace/update)
        if not is_existing_recurring_action_job and not is_recurring_action_job:
            bail_out = True
            # job_type = 'recurring job'

        if bail_out:
            # Do not need to create {type} "{name}" since {type} already exists.'.format(name=name, type=job_type)
            return

    # Create and return objects of type RecurringJob (base type)
    if not is_recurring_action_job:
        param_class = recurring_job_dict.pop("param_class")
        params = param_class.objects.create()

        logger.debug('Creating RecurringJob "{}".'.format(name))
        return RecurringJob.objects.create(parameters=params, **recurring_job_dict)

    # If the old one was a RecurringJob and the new one was a RecurringActionJob, temporarily rename it to avoid a clash
    # Safe to delete when all customers are on >= 7.0
    if is_existing_recurring_job_with_action:
        new_name = "{}_old".format(existing_recurringjob.name)
        logger.debug('Renaming pre-7.0 RecurringJob to "{}".'.format(new_name))
        existing_recurringjob.name = new_name
        existing_recurringjob.save()

    # Get the hook object, since we'll need it for RecurringActionJob
    hook_name = recurring_job_dict.pop("hook_name", None)
    hook = None
    if hook_name:
        try:
            hook = OrchestrationHook.objects.get(name=hook_name)
        except OrchestrationHook.DoesNotExist:
            logger.debug(
                'Cannot create recurring job "{}" for an action that does not exist ({}).'.format(
                    name, hook_name
                )
            )
            return

    # Create objects of type RecurringActionJob (descendant of RecurringJob), but defer returning it until after cleanup
    logger.debug(
        'Creating RecurringActionJob "{}" from hook named "{}".'.format(name, hook_name)
    )
    recurring_job_dict["type"] = hook.type_slug
    recurring_job_dict["hook"] = hook
    if "arguments" in recurring_job_dict:
        recurring_job_dict.pop("arguments", None)
    recurring_job = RecurringActionJob.objects.create(**recurring_job_dict)

    # If the old one was a RecurringJob and the new one was a RecurringActionJob, copy attrs and delete the RecurringJob
    # Safe to delete when all customers are on >= 7.0
    if is_existing_recurring_job_with_action:
        logger.debug(
            'Migrating pre-7.0 RecurringJob "{}" to recently created RecurringActionJob.'.format(
                name
            )
        )
        # Copy updated schedule.
        if recurring_job.schedule != existing_recurringjob.schedule:
            recurring_job.schedule = existing_recurringjob.schedule

        # Copy updated Enabled/Disabled state.
        if recurring_job.enabled != existing_recurringjob.enabled:
            recurring_job.enabled = existing_recurringjob.enabled

        # Move previously-spawned jobs under RecurringJob to the RecurringActionJob.
        # Note: we don't associate the old JobParameters to RecurringActionJob, because they don't apply in this case.
        if existing_recurringjob.spawned_jobs.exists():
            for job in existing_recurringjob.spawned_jobs.all():
                job.recurring_job = recurring_job
                job.save()

        recurring_job.save()

        # Delete the deprecated objects.
        existing_recurringjob.delete()

    return recurring_job


def create_recurring_jobs(recurring_jobs, skip=None):
    for recurring_job in recurring_jobs:
        create_recurring_job(recurring_job)


def create_content_library(content_library, skip=None):
    from utilities.models import ConnectionInfo

    ci, _ = ConnectionInfo.objects.get_or_create(name=content_library["name"])
    ci.ip = content_library["ip"]
    ci.port = content_library["port"]
    ci.protocol = content_library["protocol"]
    ci.save()


def create_field_dependencies(field_dependencies, skip=None):
    c2.create_field_dependencies(field_dependencies, skip=skip)


def create_all_dataprotection_technologies(data_protection, skip=None):
    for solution in data_protection:
        solution = solution.copy()
        name = solution.pop("name")
        c2.create_dataprotection_technology(name, **solution)


def create_tenant_permissions(tenant_permissions, skip=None):
    for perm in tenant_permissions:
        # Need to copy the dict to maintain the original dict in cb_minimal, otherwise unit tests fail since they use the cb_minimal dict's.
        perm = perm.copy()
        perm_name = perm.pop("name")
        TenantPermission.objects.update_or_create(defaults=perm, name=perm_name)


def create_tenant_roles(tenant_roles, skip=None):
    available_permissions = TenantPermission.objects.all()

    for role in tenant_roles:
        role = role.copy()
        perms = role.pop("permissions")
        role_name = role.pop("name")
        tr, created = TenantRole.objects.get_or_create(name=role_name, defaults=role)
        # TODO: if we ever want to remove perms from the OOTB
        if created:
            if perms[0] == "*":
                tr.permissions.add(*list(available_permissions))
            else:
                tr.permissions.add(*list(available_permissions.filter(name__in=perms)))


def main(objects_module, skip_steps=[]):
    """
    Load specified cb objects file and create its objects.

    `skip_steps` is an optional list of step names to be skipped. Useful when
    running database-backed unit tests that only need some of our dev fixture
    objects.
    """
    logger.debug(
        "Loading objects to create from {} module\n\n".format(objects_module.__name__)
    )
    # make sure CITConf always exist
    CITConf.get_singleton()

    steps = [
        "features",
        "gp",
        "content_library",
        "all_cfs",
        "all_cfvs",
        "all_cfos",
        "all_preconfigs",
        # creation of OSFamilies must happen before OSBuilds & Global CFVs
        "os_families",
        "all_global_cfvs",
        "data_centers",
        "all_vsphere_networks",
        "all_load_balancer_technologies",
        "all_resource_technologies",
        "all_prov_technologies",
        "all_orchestration_technologies",
        "all_container_technologies",
        "all_ipam_technologies",
        "all_itsm_technologies",
        "all_network_virtualization_technologies",
        "all_dataprotection_technologies",
        "all_orchestration_engines",
        "all_osbuilds",
        "all_swpol",
        "all_groups",
        "all_environments",
        "hook_points",
        "hooks",
        "rules",
        "all_permissions",
        "all_special_roles",
        "all_grouptype_roles",
        "all_superusers",
        "all_normalusers",
        "global_resource_pools",
        "jasper_reporting_engines",
        "all_blueprints",
        "portals",
        "static_pages",
        "recurring_jobs",
        "field_dependencies",
        "tenant_permissions",
        "tenant_roles",
    ]

    for step in steps:
        if hasattr(objects_module, step) and step not in skip_steps:
            definition = getattr(objects_module, step)
            logger.debug("Creating {}".format(step))
            globals()["create_{}".format(step)](definition, skip=skip_steps)
        else:
            logger.debug("# Skipping {}".format(step))

    set_rates(objects_module)

    run_external_create_routines = getattr(
        objects_module, "run_external_create_routines", None
    )
    if run_external_create_routines:
        logger.debug("Creating objects specified by external routines")
        run_external_create_routines()


if __name__ == "__main__":
    objects_files = []
    if len(sys.argv) == 2:
        # Use the file passed in and don't try to access the product license, which
        # may not be loaded into the databse yet
        objects_files = [sys.argv[1]]
    else:
        logger.debug(
            "No objects file specified. Objects for all available personalities will be loaded."
        )
        logger.debug("You may provide a path to the object file to load.")
        logger.debug(
            'Ex: "/opt/cloudbolt/initialize/create_objects.py /tmp/cb_objects.py"'
        )
        if has_personality(ProductTypeEnum.CMP.value):
            objects_files.append("cb_minimal.py")
        if has_personality(ProductTypeEnum.FUSE.value):
            objects_files.append("fuse_minimal.py")

        objects_files = [
            os.path.join(create_objects_dir, obj_file) for obj_file in objects_files
        ]

    if not objects_files:
        logger.debug(
            "No objects files specified and no active personalities available. Skipping."
        )

    for obj_file in objects_files:
        logger.info("Loading {} into cb_objects module".format(obj_file))
        cb_objects = SourceFileLoader("cb_objects", obj_file).load_module()

        main(cb_objects)
    sys.exit(0)
