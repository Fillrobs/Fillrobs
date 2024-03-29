# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-04-19 00:21
from __future__ import unicode_literals

from django.db import migrations, models


def setup_amd_feature_ux(apps, schema_editor):
    """
    Make Azure Managed Disks the default and set up a decent UX around still being able to choose a
    custom storage account.

    Because this migration runs before create_objects, the new azure_minimal object
    custom_storage_account_arm does not exist yet. That's why we create the new parameter here.
    """
    AzureARMHandler = apps.get_model('azure_arm', 'AzureARMHandler')
    CustomField = apps.get_model('infrastructure', 'CustomField')
    Environment = apps.get_model('infrastructure', 'Environment')
    FieldDependency = apps.get_model('infrastructure', 'FieldDependency')
    ControlValue = apps.get_model('infrastructure', 'ControlValue')
    CustomFieldMapping = apps.get_model('behavior_mapping', 'CustomFieldMapping')
    SequencedItem = apps.get_model('behavior_mapping', 'SequencedItem')
    CustomFieldValue = apps.get_model('orders', 'CustomFieldValue')

    cf_csa, created = CustomField.objects.get_or_create(
        name='custom_storage_account_arm',
        defaults={
            'label': 'Use custom storage account',
            'type': 'BOOL',
            'description': (
                "If true, specify an existing Azure storage account to be used or let one be created automatically; "
                "otherwise, Azure will manage disks and storage accounts automatically."
            ),
        }
    )
    # Get or create in case customer has deleted it
    cf_storage_account, created = CustomField.objects.get_or_create(
        name='storage_account_arm',
        defaults={
            'label': 'Azure Storage Account',
            'type': 'STR',
            'required': False,
            'description': "Location for storing VM disks."
        }
    )

    set_global_default(cf_csa, False, CustomFieldMapping, CustomFieldValue)
    add_param_to_all_azure_envs(cf_csa, AzureARMHandler, Environment)
    set_up_param_dependency(
        cf_csa, True, cf_storage_account, CustomFieldValue, ControlValue, FieldDependency)


def set_global_default(cf, value, CustomFieldMapping, CustomFieldValue):
    """
    This function does the same thing this call would do if it were available:
        cf_csa.set_global_default(False, overwrite=False)
    """
    print('set global default for {} to {}'.format(cf.name, value))
    cfv, created = CustomFieldValue.objects.get_or_create(field=cf, boolean_value=value)

    cfm = CustomFieldMapping.global_mappings.filter(custom_field=cf, os_family=None).first()
    if cfm is None:
        cfm = CustomFieldMapping.objects.create(custom_field=cf, os_family=None)

    if cfm.default:
        print("There's already a global default set for this parameter; skipping.")
        return

    cfm.default = cfv
    cfm.save()


def add_param_to_all_azure_envs(cf_csa, AzureARMHandler, Environment):
    """
    This is like importing this new tech-specific param into each env, so admins don't have to.
    """
    print('add param {} to all Azure envs'.format(cf_csa.name))
    azure_handlers = AzureARMHandler.objects.all()
    azure_envs = Environment.objects.filter(resource_handler__in=azure_handlers)
    for env in azure_envs:
        print(env.name)
        env.custom_fields.add(cf_csa)


def set_up_param_dependency(controlling_field, controlling_value, dependent_field,
                            CustomFieldValue, ControlValue, FieldDependency):
    """
    Make storage_account_arm special param dependent on custom_storage_account_arm. Only show when
    the checkbox is checked.
    """
    print('set up param dependency: only show {} when {} is {}'.format(
        dependent_field.name, controlling_field.name, controlling_value))
    dep = FieldDependency.objects.create(
        controlling_field=controlling_field,
        dependent_field=dependent_field,
        dependency_type='SHOWHIDE',
    )

    controlling_cfv, created = CustomFieldValue.objects.get_or_create(
        field=controlling_field, boolean_value=controlling_value)

    ControlValue.objects.create(field_dependency=dep, custom_field_value=controlling_cfv)


class Migration(migrations.Migration):

    dependencies = [
        ('azure_arm', '0022_auto_20180413_1815'),
        ('behavior_mapping', '0009_auto_20180119_1931'),
        ('infrastructure', '0031_add_auto_delete_ebs_volumes_parameter_to_aws_envs_20180328_1747'),
        ('orders', '0021_auto_20180202_1944'),
    ]

    operations = [
        migrations.RunPython(setup_amd_feature_ux),
    ]
