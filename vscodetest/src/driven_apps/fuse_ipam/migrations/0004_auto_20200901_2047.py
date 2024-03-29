# Generated by Django 2.2.10 on 2020-09-01 20:47

import common.fields
from django.db import migrations
import driven_apps.common.validators
import driven_apps.fuse_ipam.validators.infoblox_ipam_policy_validators


class Migration(migrations.Migration):

    dependencies = [
        ('fuse_ipam', '0003_merge_20200821_2045'),
    ]

    operations = [
        migrations.AddField(
            model_name='infobloxipampolicy',
            name='fixed_address_record_template',
            field=common.fields.TemplatableField(blank=True, help_text='A json dict detailing the template for the fixed address record in Infoblox IPAM', max_length=65536, validators=[driven_apps.common.validators.StringFieldValidator(blank=True, field_name='fixedAddressRecordTemplate', template=True), driven_apps.fuse_ipam.validators.infoblox_ipam_policy_validators.FixedAddressRecordTemplateValidator(field_name='fixedAddressRecordTemplate')]),
        ),
        migrations.AddField(
            model_name='infobloxipampolicy',
            name='network_view',
            field=common.fields.TemplatableField(default='default', help_text='The name of the network view in Infoblox IPAM', max_length=65536, validators=[driven_apps.common.validators.StringFieldValidator(blank=True, field_name='networkView', template=True)]),
            preserve_default=False,
        ),
    ]
