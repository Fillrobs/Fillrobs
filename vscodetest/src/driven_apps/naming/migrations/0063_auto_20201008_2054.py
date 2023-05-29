# Generated by Django 2.2.10 on 2020-10-08 20:54

from django.db import migrations, models
import driven_apps.common.validators


class Migration(migrations.Migration):

    dependencies = [
        ('naming', '0062_auto_20201007_2155'),
    ]

    operations = [
        migrations.AlterField(
            model_name='microsoftendpoint',
            name='microsoft_version',
            field=models.CharField(help_text='The Microsoft version for this endpoint.', max_length=32, null=True, validators=[driven_apps.common.validators.RequiredFieldValidator(allow_null=True, field_name='microsoftVersion'), driven_apps.common.validators.MinLengthValidator(constraint=1, field_name='microsoftVersion', required=False), driven_apps.common.validators.OneOfValidator(allowed_values=['2019'], field_name='microsoftVersion')]),
        ),
    ]
