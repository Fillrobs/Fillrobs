# Generated by Django 2.2.10 on 2020-09-21 17:20

import common.fields
from django.db import migrations
import django_extensions.db.fields.json
import driven_apps.common.validators


class Migration(migrations.Migration):

    dependencies = [
        ('naming', '0050_bluecatendpoint_ip_address_record_user_defined_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='bluecatendpoint',
            name='dns_view',
            field=common.fields.TemplatableField(default='default', help_text='(Templatable) DNS View.', max_length=65536, validators=[driven_apps.common.validators.StringFieldValidator(blank=False, field_name='dnsView', template=True)]),
        ),
        migrations.AddField(
            model_name='bluecatendpoint',
            name='host_record_user_defined_fields',
            field=django_extensions.db.fields.json.JSONField(blank=True, default=dict, help_text='Host record user defined field.', null=True),
        ),
        migrations.AlterField(
            model_name='infobloxendpoint',
            name='dns_view',
            field=common.fields.TemplatableField(default='default', help_text='(Templatable) DNS View.', max_length=65536, validators=[driven_apps.common.validators.StringFieldValidator(blank=False, field_name='dnsView', template=True)]),
        ),
    ]
