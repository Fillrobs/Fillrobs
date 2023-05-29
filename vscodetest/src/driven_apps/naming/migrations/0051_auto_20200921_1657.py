# Generated by Django 2.2.10 on 2020-09-21 16:57

import common.fields
from django.db import migrations
import driven_apps.common.validators


class Migration(migrations.Migration):

    dependencies = [
        ('naming', '0050_bluecatendpoint_ip_address_record_user_defined_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bluecatendpoint',
            name='configuration_name',
            field=common.fields.TemplatableField(help_text='BlueCat configuration context.', max_length=65536, validators=[driven_apps.common.validators.StringFieldValidator(blank=False, field_name='configurationName', template=True)]),
        ),
    ]
