# Generated by Django 2.2.12 on 2020-05-20 22:48

import cb_secrets.fields
import common.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('externalcontent', '0016_set_app_ids_20190923_1137'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('infrastructure', '0051_auto_20200109_1803'),
    ]

    operations = [
        migrations.CreateModel(
            name='ITSMTechnology',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Name of the itsm technology (ex. ServiceNow)')),
                ('version', models.CharField(max_length=20, verbose_name='Version of the itsm technology')),
                ('modulename', models.CharField(blank=1, max_length=50, verbose_name='Python module for interacting with this version of this itsm technology.')),
            ],
            options={
                'verbose_name_plural': 'ITSM technologies',
            },
        ),
        migrations.CreateModel(
            name='ITSM',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.CharField(max_length=50, verbose_name='IP Address')),
                ('port', models.IntegerField(default=443, help_text='Port used to connect to this itsm.', validators=[common.validators.is_only_digits])),
                ('protocol', models.CharField(choices=[('http', 'http'), ('https', 'https')], default='https', help_text='Protocol used to connect to this itsm.', max_length=10)),
                ('service_account', models.CharField(max_length=250, verbose_name='Account username')),
                ('password', cb_secrets.fields.EncryptedPasswordField(verbose_name='Account password')),
                ('name', models.CharField(blank=True, max_length=50, null=True)),
                ('environment', models.ManyToManyField(blank=True, to='infrastructure.Environment')),
                ('itsm_technology', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='itsm.ITSMTechnology')),
                ('real_type', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to='contenttypes.ContentType')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CMDB',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('environment', models.ManyToManyField(blank=True, to='infrastructure.Environment')),
                ('itsm', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='itsm.ITSM')),
                ('osbuild', models.ManyToManyField(blank=True, to='externalcontent.OSBuild')),
            ],
        ),
    ]
