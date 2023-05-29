# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import connectors.puppet.models
import django.db.models.deletion
import cb_secrets.fields


class Migration(migrations.Migration):

    dependencies = [
        ('connectors', '0001_initial'),
        ('infrastructure', '0001_initial'),
        ('utilities', '0001_initial'),
        ('externalcontent', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PEConf',
            fields=[
                ('connectorconf_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='connectors.ConnectorConf', on_delete=models.CASCADE)),
                ('hostname', models.CharField(default='puppet', help_text='PE master hostname', max_length=255)),
                ('cert_state', models.CharField(default='Uninitialized', max_length=255, choices=[('Uninitialized', 'Uninitialized'), ('Generate Cert Error', 'Generate Cert Error'), ('Generate Cert Done', 'Generate Cert Done'), ('Generate CSR Error', 'Generate CSR Error'), ('Generate CSR Done', 'Generate CSR Done'), ('Send CSR Error', 'Send CSR Error'), ('Send CSR Done', 'Send CSR Done'), ('Fetch Signed Cert Error', 'Fetch Signed Cert Error'), ('Fetch Signed Cert Done', 'Fetch Signed Cert Done'), ('Installed Signed Cert Error', 'Installed Signed Cert Error'), ('Installed Signed Cert Done', 'Installed Signed Cert Done')])),
                ('cert_message', models.TextField(null=True, blank=True)),
                ('environment', models.CharField(default='production', help_text='PE environment name', max_length=255)),
                ('cert_name', models.CharField(max_length=255, null=True, blank=True)),
                ('ssl_signed_cert', models.TextField(help_text='Signed SSL Client Certificate', null=True, blank=True)),
                ('ssl_private_key', cb_secrets.fields.EncryptedPasswordField(help_text='Private SSL Client Key', null=True, blank=True)),
                ('ssl_cacert', models.TextField(help_text='CA Certificate', null=True, blank=True)),
                ('version', models.CharField(default='2015.3', max_length=10, choices=[('3.X', '3.X'), ('2015.3', '2015+')])),
                ('master_api_connection', models.ForeignKey(related_name='master_api_connections', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='utilities.ConnectionInfo', help_text='Master API Connection EndPoint', null=True)),
                ('master_server', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='infrastructure.Server', help_text='Puppet Master Server in CB', null=True)),
                ('master_ssh_connection', models.ForeignKey(related_name='master_ssh_connections', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='utilities.ConnectionInfo', help_text='Master SSH Connection EndPoint', null=True)),
            ],
            options={
                'verbose_name': 'PE Configuration',
            },
            bases=('connectors.connectorconf',),
        ),
        migrations.CreateModel(
            name='PEGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='Name of the Puppet Group', max_length=255)),
                ('uuid', models.CharField(help_text='Puppet Enterprise UUID for this Group.', max_length=255)),
                ('cb_application', models.ForeignKey(verbose_name='Application', to='externalcontent.Application', help_text='Associated Application in CloudBolt', on_delete=models.CASCADE)),
                ('pe_conf', models.ForeignKey(to='puppet_ent.PEConf', on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name': 'PE Group',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PENode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('certname', models.CharField(help_text="The Node's certname (FQDN by default)", max_length=255)),
                ('_facts', models.TextField(default='{}', help_text="This PuppetNode's most recent Facter data stored as JSON", null=True, blank=True)),
                ('cb_server', models.OneToOneField(related_name='pe_node', null=True, blank=True, to='infrastructure.Server', on_delete=models.SET_NULL)),
                ('conf', models.ForeignKey(related_name='nodes', to='puppet_ent.PEConf', help_text='The PE Config that manages this PE Node.', on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name': 'PE Node',
            },
            bases=(models.Model, connectors.puppet.models.GenericPuppetNodeMixin),
        ),
        migrations.CreateModel(
            name='PEReport',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('yaml', models.TextField(default='')),
                ('host', models.CharField(max_length=255)),
                ('time', models.DateTimeField()),
                ('time_received', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(max_length=20, choices=[('failed', 'Failed'), ('changed', 'Changed'), ('unchanged', 'Unchanged')])),
                ('conf', models.ForeignKey(related_name='reports', to='puppet_ent.PEConf', help_text='The PEConf whose master submitted this report.', on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ['time'],
                'get_latest_by': 'time',
            },
            bases=(connectors.puppet.models.GenericPuppetReportMixin, models.Model),
        ),
    ]
