# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import cb_secrets.fields
import common.validators


class Migration(migrations.Migration):

    dependencies = [
        ('infrastructure', '0002_serverexpireparameters_servernetworkcard_serversnapshot'),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProvisionEngine',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('ip', models.CharField(max_length=50, verbose_name='IP address')),
                ('port', models.IntegerField(verbose_name='TCP Port', validators=[common.validators.is_only_digits])),
                ('protocol', models.CharField(max_length=10, verbose_name='Protocol used to connect to this prov engine', choices=[('http', 'http'), ('https', 'https'), ('ssh', 'ssh')])),
                ('serviceaccount', models.CharField(max_length=50, verbose_name='Account with authorization to connect and run commands')),
                ('servicepasswd', cb_secrets.fields.EncryptedPasswordField(help_text='For security reasons, this password must be entered each time the object is modified.', verbose_name='Account password to be used to run commands on this prov engine')),
                ('custom_fields', models.ManyToManyField(to='infrastructure.CustomField', null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProvisionTechnology',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, verbose_name='Name of the prov engine technology (ex. HP Server Automation)')),
                ('version', models.CharField(max_length=20, null=1, verbose_name='Version of the prov engine technology', blank=1)),
            ],
            options={
                'verbose_name_plural': 'Provisioning technologies',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='provisionengine',
            name='provision_technology',
            field=models.ForeignKey(to='provisionengines.ProvisionTechnology', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='provisionengine',
            name='real_type',
            field=models.ForeignKey(editable=False, to='contenttypes.ContentType', null=True, on_delete=models.SET_NULL),
            preserve_default=True,
        ),
    ]
