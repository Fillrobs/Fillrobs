# Generated by Django 2.2.10 on 2020-07-14 23:23

from django.db import migrations
import driven_apps.common.custom_fields
import driven_apps.common.validators


class Migration(migrations.Migration):

    dependencies = [
        ('validators', '0010_auto_20200706_1859'),
    ]

    operations = [
        migrations.AlterField(
            model_name='validator',
            name='type',
            field=driven_apps.common.custom_fields.LowerCaseCharField(help_text='The type of this validator.', max_length=64, validators=[driven_apps.common.validators.RequiredFieldValidator(field_name='type'), driven_apps.common.validators.OneOfValidator(allowed_values=['dns', 'microsoft', 'vra7', 'vra8'], field_name='type')]),
        ),
    ]
