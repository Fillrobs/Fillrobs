# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-03-28 17:47
from __future__ import unicode_literals

from django.db import migrations


def add_auto_delete_volumes_param(apps, schema_editor):
    """
    Get or create the 'delete_ebs_volumes_on_termination' parameter,
    then add to all existing envs that don't already have it.
    """
    Environment = apps.get_model('infrastructure', 'Environment')
    CustomField = apps.get_model('infrastructure', 'CustomField')
    CustomFieldValue = apps.get_model('orders', 'CustomFieldValue')

    # make the parameter the same as it is in aws_minimal.
    cf_kwargs = {
        'name': 'delete_ebs_volumes_on_termination',
        'label': 'Auto-Delete EBS Volumes on Termination',
        'type': 'BOOL',
        'required': False,
        'description': ("When set to True, sets the attached "
                        "EBS volumes to be automatically deleted on termination of the AWS instance."),
        'show_on_servers': True,
    }

    cf, _ = CustomField.objects.get_or_create(**cf_kwargs)
    cfv, _ = CustomFieldValue.objects.get_or_create(field=cf, boolean_value=True)

    for env in Environment.objects.filter(resource_handler__resource_technology__name='Amazon Web Services'):
        # if the environment doesn't already have this parameter, then add it.
        if cf not in env.custom_fields.all():
            env.custom_fields.add(cf)
            env.custom_field_options.add(cfv)


class Migration(migrations.Migration):

    dependencies = [
        ('infrastructure', '0030_auto_20180202_1944'),
    ]

    operations = [
        migrations.RunPython(add_auto_delete_volumes_param,
                             migrations.RunPython.noop),
    ]
