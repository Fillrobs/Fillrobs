# Generated by Django 2.2.16 on 2020-11-12 15:38

import common.fields
from django.db import migrations, models
import driven_apps.common.validators


class Migration(migrations.Migration):

    dependencies = [
        ('ansible_tower', '0006_auto_20201105_2112'),
    ]

    operations = [
        migrations.AddField(
            model_name='ansibletowerpolicy',
            name='group_separator',
            field=models.CharField(default='/', help_text='Ansible Tower Group Separator.', max_length=255, validators=[driven_apps.common.validators.NotBlankValidator(field_name='groupSeparator', required=True), driven_apps.common.validators.MaxLengthValidator(constraint=1, field_name='groupSeparator', required=True)]),
        ),
        migrations.AddField(
            model_name='ansibletowerpolicy',
            name='groups',
            field=common.fields.TemplatableField(blank=True, help_text='Ansible Tower Groups.', max_length=65536, null=True, validators=[driven_apps.common.validators.StringFieldValidator(blank=True, field_name='groups', template=True)]),
        ),
    ]