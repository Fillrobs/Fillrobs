# Generated by Django 2.2.10 on 2020-09-25 14:54

import common.fields
from django.db import migrations
import driven_apps.common.validators


class Migration(migrations.Migration):

    dependencies = [
        ('fuse_ipam', '0014_merge_20200924_1632'),
    ]

    operations = [
        migrations.AddField(
            model_name='ipamreservation',
            name='hostname',
            field=common.fields.TemplatableField(blank=True, help_text='The optional host name override for this IPAM Reservation.', max_length=1023, null=True, validators=[driven_apps.common.validators.DNSNameValidator(blank=True, field_name='hostname', template=True)]),
        ),
        migrations.AlterField(
            model_name='ipampolicy',
            name='host_name_override',
            field=common.fields.TemplatableField(blank=True, default='{{request.hostname}}', help_text='The optional host name override for this IPAM policy.', max_length=65536, validators=[driven_apps.common.validators.StringFieldValidator(blank=True, field_name='hostNameOverride', template=True)]),
        ),
    ]
