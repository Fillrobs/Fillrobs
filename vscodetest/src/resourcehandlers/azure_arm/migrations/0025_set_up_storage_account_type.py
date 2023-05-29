# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-04-19 00:21
from __future__ import unicode_literals

from django.db import migrations, models
from utilities.logger import ThreadLogger


logger = ThreadLogger(__name__)


def setup_sa_type(apps, schema_editor):
    """
    Because this migration runs before create_objects, the new azure_minimal object
    storage_account_type_arm does not exist yet. That's why we get-or-create the new parameter here.
    """
    AzureARMHandler = apps.get_model('azure_arm', 'AzureARMHandler')
    CustomField = apps.get_model('infrastructure', 'CustomField')
    Environment = apps.get_model('infrastructure', 'Environment')
    CustomFieldMapping = apps.get_model('behavior_mapping', 'CustomFieldMapping')
    SequencedItem = apps.get_model('behavior_mapping', 'SequencedItem')
    CustomFieldValue = apps.get_model('orders', 'CustomFieldValue')

    cf_sa_type, created = CustomField.objects.get_or_create(
        name='storage_account_type_arm',
        defaults={
            'label': 'Storage type',
            'type': 'STR',
            'required': False,
            'description': (
                "Type of storage to be used for this server's disks: Premium (SSD-based) or Standard (HDD-based)"
            ),
        }
    )

    env_count = add_param_to_all_azure_envs(cf_sa_type, AzureARMHandler, Environment)
    if env_count:
        set_global_default(cf_sa_type, 'Standard_LRS', CustomFieldMapping, CustomFieldValue)


def set_global_default(cf, value, CustomFieldMapping, CustomFieldValue):
    """
    This function does the same thing this call would do if it were available:
        cf_csa.set_global_default(False, overwrite=False)
    """
    logger.info('Set global default for {} to {}'.format(cf.name, value))
    cfv, created = CustomFieldValue.objects.get_or_create(field=cf, str_value=value)

    cfm = CustomFieldMapping.global_mappings.filter(custom_field=cf, os_family=None).first()
    if cfm is None:
        cfm = CustomFieldMapping.objects.create(custom_field=cf, os_family=None)

    if cfm.default:
        logger.info("This parameter already has a global default: {}".format(cfm.default))
        logger.info("Skipping.")
        return

    cfm.default = cfv
    cfm.save()


def add_param_to_all_azure_envs(cf, AzureARMHandler, Environment):
    """
    This is like importing this new tech-specific param into each env, so admins don't have to.
    """
    logger.info('Add param {} to all Azure envs'.format(cf.name))
    azure_handlers = AzureARMHandler.objects.all()
    azure_envs = Environment.objects.filter(resource_handler__in=azure_handlers)
    for env in azure_envs:
        env.custom_fields.add(cf)
    return len(azure_envs)


class Migration(migrations.Migration):

    dependencies = [
        ('azure_arm', '0024_merge_20180430_1921'),
        ('behavior_mapping', '0009_auto_20180119_1931'),
        ('infrastructure', '0032_lengthen_environment_name'),
        ('orders', '0021_auto_20180202_1944'),
    ]

    operations = [
        migrations.RunPython(setup_sa_type, migrations.RunPython.noop),
    ]