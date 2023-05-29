# Generated by Django 2.2.10 on 2020-04-23 22:23

from django.db import migrations, models
import driven_apps.common.custom_fields
import driven_apps.common.validators


class Migration(migrations.Migration):

    dependencies = [
        ('naming', '0010_endpoint'),
    ]

    operations = [
        migrations.AlterField(
            model_name='endpoint',
            name='description',
            field=models.TextField(blank=True, default='', help_text='The description text for this endpoint.', validators=[driven_apps.common.validators.RequiredFieldValidator(allow_blank=True, field_name='description')]),
        ),
        migrations.AlterField(
            model_name='endpoint',
            name='host',
            field=models.CharField(help_text='The host name or IP address for this endpoint.', max_length=255, validators=[driven_apps.common.validators.RequiredFieldValidator(field_name='host'), driven_apps.common.validators.HostAddressValidator(field_name='host')]),
        ),
        migrations.AlterField(
            model_name='endpoint',
            name='name',
            field=models.CharField(help_text='The user-specified name of this endpoint.', max_length=255, validators=[driven_apps.common.validators.RequiredFieldValidator(field_name='name')]),
        ),
        migrations.AlterField(
            model_name='endpoint',
            name='port',
            field=models.IntegerField(help_text='The port number for this endpoint.', validators=[driven_apps.common.validators.RequiredFieldValidator(field_name='port'), driven_apps.common.validators.IntegerRangeValidator(1, 65535, field_name='port')]),
        ),
        migrations.AlterField(
            model_name='endpoint',
            name='type',
            field=driven_apps.common.custom_fields.LowerCaseCharField(help_text='The type of this endpoint.', max_length=64, validators=[driven_apps.common.validators.RequiredFieldValidator(field_name='type')]),
        ),
    ]
