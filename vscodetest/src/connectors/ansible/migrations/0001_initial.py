# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('connectors', '0002_auto_20160829_2059'),
        ('infrastructure', '0009_serverstats'),
        ('externalcontent', '0003_auto_20161004_2121'),
        ('utilities', '0007_auto_20161021_1441'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnsibleConf',
            fields=[
                ('connectorconf_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='connectors.ConnectorConf', on_delete=models.CASCADE)),
                ('connection_info', models.ForeignKey(blank=True, to='utilities.ConnectionInfo', help_text='Ansible Management Connection Info', null=True, on_delete=models.SET_NULL)),
            ],
            options={
                'verbose_name': 'Ansible Configuration',
            },
            bases=('connectors.connectorconf',),
        ),
        migrations.CreateModel(
            name='AnsibleGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='Name of the Ansible group', max_length=255)),
                ('cb_application', models.ForeignKey(verbose_name='Application', to='externalcontent.Application', help_text='Associated Application in CloudBolt', on_delete=models.CASCADE)),
                ('conf', models.ForeignKey(to='ansible.AnsibleConf', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AnsibleNode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('node_name', models.CharField(help_text="the node's name in Ansible (the node's FQDN by default)", max_length=255)),
                ('cb_server', models.OneToOneField(related_name='ansible_node', null=True, blank=True, to='infrastructure.Server', on_delete=models.SET_NULL)),
                ('conf', models.ForeignKey(related_name='nodes', to='ansible.AnsibleConf', help_text='The Ansible Conf that manages this Ansible Node.', on_delete=models.CASCADE)),
                ('roles', models.ManyToManyField(help_text='Groups this node belongs to.', to='ansible.AnsibleGroup')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='ansiblenode',
            unique_together=set([('node_name', 'conf')]),
        ),
        migrations.AlterUniqueTogether(
            name='ansiblegroup',
            unique_together=set([('conf', 'cb_application')]),
        ),
    ]
