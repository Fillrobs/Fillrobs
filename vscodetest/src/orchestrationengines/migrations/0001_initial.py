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
            name='OrchestrationEngine',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('scheme', models.CharField(default='https', help_text='Scheme/protocol used to connect to this orchestration engine', max_length=10, choices=[('http', 'http'), ('https', 'https')])),
                ('host', models.CharField(help_text='IP address/hostname used to connect to this orchestration engine', max_length=50)),
                ('port', models.IntegerField(default='8443', help_text='Port used to connect to this reporting engine', validators=[common.validators.is_only_digits])),
                ('serviceaccount', models.CharField(default='admin', help_text='Authorized user to list and run orchestration flows for this engine', max_length=50)),
                ('servicepasswd', cb_secrets.fields.EncryptedPasswordField(help_text='Password for authorized user to list and run orchestration flows for this engine')),
                ('real_type', models.ForeignKey(editable=False, to='contenttypes.ContentType', null=True, on_delete=models.SET_NULL)),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OrchestrationFlow',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('uuid', models.CharField(max_length=100, null=True, blank=True)),
                ('expose_as_server_action', models.BooleanField(default=False)),
                ('timeout', models.IntegerField(default=5, help_text='Minutes to wait for flow to complete before marking it a failure.', validators=[common.validators.is_only_digits])),
                ('engine', models.ForeignKey(to='orchestrationengines.OrchestrationEngine', on_delete=models.CASCADE)),
                ('environments', models.ManyToManyField(related_name='flows', null=True, to='infrastructure.Environment', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OrchestrationFlowParameters',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('param_key', models.CharField(max_length=50)),
                ('param_c2_mapping', models.CharField(max_length=100, null=True, blank=True)),
                ('param_required', models.BooleanField(default=False)),
                ('flow', models.ForeignKey(related_name='parameters', to='orchestrationengines.OrchestrationFlow', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OrchestrationTechnology',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, verbose_name='Name of the orchestration technology (ex. HP Operations Orchestration)')),
                ('version', models.CharField(max_length=20, verbose_name='Version of the technology api')),
                ('modulename', models.CharField(max_length=50, verbose_name='Python module for interacting with this version of this technology.', blank=True)),
            ],
            options={
                'verbose_name_plural': 'Orchestration technologies',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='orchestrationengine',
            name='technology',
            field=models.ForeignKey(to='orchestrationengines.OrchestrationTechnology', on_delete=models.CASCADE),
            preserve_default=True,
        ),
    ]
