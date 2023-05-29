# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-06-06 16:54
from __future__ import unicode_literals

from django.db import migrations


def set_up_volume_type_on_aws_envs(apps, schema_editor):
    """

    :param apps:
    :param schema_editor:
    :return:
    """
    CustomField = apps.get_model('infrastructure', 'CustomField')
    CustomFieldValue = apps.get_model('orders', 'CustomFieldValue')
    Environment = apps.get_model('infrastructure', 'Environment')

    ebs_volume_type_dict = {
            'name': 'ebs_volume_type',
            'defaults': {
                'label': 'EBS Volume Type',
                'type': 'STR',
                'required': True,
                'description': (
                    "Specifies the type of disk. This determines the performance and cost of the disk. "
                    "See https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EBSVolumeTypes.html for more info "
                    "on disk types."
                ),
                'show_on_servers': True,
            }
        }

    iops_dict = {
        'name': 'iops',
        'defaults': {
            'label': 'IOPS',
            'type': 'INT',
            'required': False,
            'description': "Input/output operations per second. AWS requires you to specify an amount of IOPS when "
                           "creating an 'io1' volume.",
        }
    }

    # get or create the custom fields
    ebs_volume_type_cf, created_volume_type = CustomField.objects.get_or_create(**ebs_volume_type_dict)
    iops_cf, created_iops = CustomField.objects.get_or_create(**iops_dict)

    # Make ebs_volume_type required if we didn't just create it.
    if not created_volume_type:
        ebs_volume_type_cf.required = True
        ebs_volume_type_cf.save()

    # Create options for ebs_volume_type.
    volume_type_cfvs = []
    volume_type_options = ['standard', 'gp2', 'io1', 'st1', 'sc1']
    for option in volume_type_options:
        cfv, _ = CustomFieldValue.objects.get_or_create(field=ebs_volume_type_cf, str_value=option)
        volume_type_cfvs.append(cfv)

    # Add ebs_volume_type, its options, and iops to all existing AWS environments.
    aws_envs = Environment.objects.filter(resource_handler__resource_technology__name='Amazon Web Services')
    for env in aws_envs:
        env.custom_fields.add(ebs_volume_type_cf)
        env.custom_fields.add(iops_cf)
        env.custom_field_options.add(*volume_type_cfvs)
        env.save()


class Migration(migrations.Migration):

    dependencies = [
        ('aws', '0006_ebsdisk_volume_type'),
    ]

    operations = [
        migrations.RunPython(
            set_up_volume_type_on_aws_envs,
            migrations.RunPython.noop),
    ]
