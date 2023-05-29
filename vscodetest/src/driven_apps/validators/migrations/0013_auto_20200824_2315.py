# Generated by Django 2.2.10 on 2020-08-24 23:15

from django.db import migrations
import driven_apps.common.custom_fields
import driven_apps.common.validators


class Migration(migrations.Migration):

    dependencies = [
        ('validators', '0012_auto_20200824_2007'),
    ]

    operations = [
        migrations.AlterField(
            model_name='validator',
            name='type',
            field=driven_apps.common.custom_fields.LowerCaseCharField(help_text='The type of this validator.', max_length=64, validators=[driven_apps.common.validators.RequiredFieldValidator(field_name='type'), driven_apps.common.validators.OneOfValidator(allowed_values=['dns', 'men_and_mice', 'microsoft', 'vra7', 'vra8'], field_name='type')]),
        ),
    ]
