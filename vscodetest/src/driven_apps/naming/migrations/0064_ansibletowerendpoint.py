# Generated by Django 2.2.10 on 2020-10-16 17:06

from django.db import migrations, models
import django.db.models.deletion
import driven_apps.common.validators


class Migration(migrations.Migration):

    dependencies = [
        ('credentials', '0003_modulecredential_connection_method'),
        ('naming', '0063_auto_20201008_2054'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnsibleTowerEndpoint',
            fields=[
                ('endpoint_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='naming.Endpoint')),
                ('host', models.CharField(help_text='The host name or IP address for this endpoint.', max_length=255, validators=[driven_apps.common.validators.RequiredFieldValidator(field_name='host'), driven_apps.common.validators.HostAddressValidator(field_name='host')])),
                ('port', models.IntegerField(help_text='The port number for this endpoint.', validators=[driven_apps.common.validators.RequiredFieldValidator(field_name='port'), driven_apps.common.validators.IntegerRangeValidator(1, 65535, field_name='port')])),
                ('ssl', models.BooleanField(default=False, help_text='Flag to enable SSL for this endpoint.', validators=[driven_apps.common.validators.RequiredFieldValidator(field_name='ssl'), driven_apps.common.validators.BooleanFieldValidator(field_name='ssl')])),
                ('ansible_tower_version', models.CharField(help_text='Ansible Tower version for this endpoint.', max_length=32, null=True, validators=[driven_apps.common.validators.RequiredFieldValidator(allow_null=True, field_name='ansibleTowerVersion'), driven_apps.common.validators.MinLengthValidator(constraint=1, field_name='ansibleTowerVersion', required=False), driven_apps.common.validators.OneOfValidator(allowed_values=['3.5'], field_name='ansibleTowerVersion')])),
                ('credential', models.ForeignKey(help_text='Credential for this endpoint.', on_delete=django.db.models.deletion.PROTECT, to='credentials.ModuleCredential')),
            ],
            options={
                'db_table': 'endpoints_ansible_tower',
                'ordering': ['id'],
                'abstract': False,
            },
            bases=('naming.endpoint', models.Model),
        ),
    ]
