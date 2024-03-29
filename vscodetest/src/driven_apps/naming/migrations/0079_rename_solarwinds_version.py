# Generated by Django 2.2.16 on 2021-04-06 21:42

from django.db import migrations, models
import driven_apps.common.validators


class Migration(migrations.Migration):

    dependencies = [
        ('naming', '0078_remove_solarwindsendpoint_skip_ip_address_scanning'),
    ]

    operations = [
        migrations.RenameField(
            model_name='solarwindsendpoint',
            old_name='version',
            new_name='solarwinds_version'
        ),
        migrations.AlterField(
            model_name='solarwindsendpoint',
            name='solarwinds_version',
            field=models.CharField(default='4.6', help_text='The SolarWinds version for this endpoint.', max_length=32,
                                   validators=[driven_apps.common.validators.RequiredFieldValidator(
                                       field_name='solarwindsVersion'),
                                       driven_apps.common.validators.MinLengthValidator(constraint=1,
                                                                                        field_name='solarwindsVersion',
                                                                                        required=True),
                                       driven_apps.common.validators.OneOfValidator(
                                           allowed_values=['4.6', '4.7', '4.8', '4.9', '2020.2'],
                                           field_name='solarwindsVersion')])
        ),
    ]
