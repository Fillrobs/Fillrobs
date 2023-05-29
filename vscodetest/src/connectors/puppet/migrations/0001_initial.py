# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import connectors.puppet.models


class Migration(migrations.Migration):

    dependencies = [
        ('connectors', '0001_initial'),
        ('infrastructure', '0001_initial'),
        ('externalcontent', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PuppetClass',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='Name of the Puppet class on the Puppet Master', max_length=255)),
                ('cb_application', models.ForeignKey(verbose_name='Application', to='externalcontent.Application', help_text='Associated Application in CloudBolt', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PuppetConf',
            fields=[
                ('connectorconf_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='connectors.ConnectorConf', on_delete=models.CASCADE)),
                ('hostname', models.CharField(default='puppet', help_text="Puppet master's hostname", max_length=255)),
                ('environment', models.CharField(default='production', help_text='Puppet environment name', max_length=255, verbose_name='Puppet environment')),
                ('cert_name', models.CharField(help_text='Basename of the various SSL artifacts generated to get to the signed SSL certificate for this CB instance.', max_length=255, null=True, blank=True)),
                ('cert_state', models.CharField(default='Not started', max_length=255, choices=[('Not started', 'Not started'), ('Create Cert Directory Error', 'Create Cert Directory Error'), ('Create Cert Directory Done', 'Create Cert Directory Done'), ('Generate Cert Error', 'Generate Cert Error'), ('Generate Cert Done', 'Generate Cert Done'), ('Generate CSR Error', 'Generate CSR Error'), ('Generate CSR Done', 'Generate CSR Done'), ('Send CSR Error', 'Send CSR Error'), ('Send CSR Done', 'Send CSR Done'), ('Fetch Signed Cert Error', 'Fetch Signed Cert Error'), ('Fetch Signed Cert Done', 'Fetch Signed Cert Done'), ('Installed Signed Cert Error', 'Installed Signed Cert Error'), ('Installed Signed Cert Done', 'Installed Signed Cert Done')])),
                ('cert_message', models.TextField(null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('connectors.connectorconf',),
        ),
        migrations.CreateModel(
            name='PuppetNode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('certname', models.CharField(help_text="the node's certname (the node's FQDN by default)", max_length=255)),
                ('_facts', models.TextField(default='{}', help_text="This PuppetNode's most recent Facter data stored as JSON", null=True, blank=True)),
                ('cb_server', models.OneToOneField(related_name='puppet_node', null=True, blank=True, to='infrastructure.Server', on_delete=models.SET_NULL)),
                ('conf', models.ForeignKey(related_name='nodes', to='puppet.PuppetConf', help_text='The Puppet Conf that manages this Puppet Node.', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(connectors.puppet.models.GenericPuppetNodeMixin, models.Model),
        ),
        migrations.CreateModel(
            name='PuppetReport',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('yaml', models.TextField()),
                ('host', models.CharField(max_length=255)),
                ('time', models.DateTimeField()),
                ('time_received', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(max_length=20, choices=[('failed', 'Failed'), ('changed', 'Changed'), ('unchanged', 'Unchanged')])),
                ('conf', models.ForeignKey(related_name='reports', to='puppet.PuppetConf', help_text='The PuppetConf whose master submitted this report.', on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ['time'],
                'get_latest_by': 'time',
            },
            bases=(connectors.puppet.models.GenericPuppetReportMixin, models.Model),
        ),
        migrations.AlterUniqueTogether(
            name='puppetnode',
            unique_together=set([('certname', 'conf')]),
        ),
        migrations.AddField(
            model_name='puppetclass',
            name='puppet_conf',
            field=models.ForeignKey(to='puppet.PuppetConf', on_delete=models.CASCADE),
            preserve_default=True,
        ),
    ]
