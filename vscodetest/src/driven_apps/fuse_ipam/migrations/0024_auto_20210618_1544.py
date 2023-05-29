# Generated by Django 3.2.3 on 2021-06-18 15:44

import common.fields
from django.db import migrations, models
import driven_apps.common.validators


class Migration(migrations.Migration):

    dependencies = [
        ('fuse_ipam', '0023_microsoftipampolicy'),
    ]

    operations = [
        migrations.AddField(
            model_name='ipampolicy',
            name='conflict_name_template',
            field=common.fields.TemplatableField(blank=True, help_text='The Name Template to be used if a conflict is found and the assigned IP is in use', max_length=65536, null=True, validators=[driven_apps.common.validators.StringFieldValidator(blank=True, field_name='conflict_name_template', template=True)]),
        ),
        migrations.AddField(
            model_name='ipampolicy',
            name='update_conflict_name_with_dns',
            field=models.BooleanField(default=False, help_text='If true and name is discovered with DNS, use that name to update the IPAM record, instead of the conflict_name_template'),
        ),
    ]