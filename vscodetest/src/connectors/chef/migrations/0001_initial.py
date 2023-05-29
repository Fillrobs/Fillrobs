# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import common.validators


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('connectors', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChefConf',
            fields=[
                ('connectorconf_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='connectors.ConnectorConf', on_delete=models.CASCADE)),
                ('hostname', models.CharField(help_text="Chef server's hostname or IP.  For hosted Chef, this should be set to 'api.opscode.com'", max_length=255)),
                ('c2_client_name', models.CharField(help_text='The client name in Chef for the CB server (the name given to <client_name>.pem generated during the installation of knife on the CB server)', max_length=255, verbose_name='CB client name')),
                ('organization_name', models.CharField(default='', help_text='For Enterprise Chef, the name of the organization for this Chef connector (if more than one Chef organization is used, create a Chef connector for each)', max_length=255, blank=True)),
                ('knife_bootstrap_additional_args', models.TextField(help_text="Additional command line arguments to pass when installing Chef agents with knife bootstrap.  Supports the use of templetized values. Ex. '-N {{server.hostname}} -r chef-client,apt'", blank=True)),
                ('port', models.IntegerField(default=443, validators=[common.validators.is_only_digits])),
                ('protocol', models.CharField(default='https', max_length=10, choices=[('http', 'http'), ('https', 'https')])),
            ],
            options={
                'abstract': False,
            },
            bases=('connectors.connectorconf',),
        ),
        migrations.CreateModel(
            name='ChefCookbook',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='Name of the Chef cookbook on the Chef server', max_length=255)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ChefNode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('node_name', models.CharField(help_text="the node's name in Chef, as set in /etc/chef/client.rb (the node's FQDN by default,)", max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ChefRole',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='Name of the Chef cookbook on the Chef server', max_length=255)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CommunityCookbook',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=50)),
                ('category', models.CharField(max_length=50, blank=True)),
                ('average_rating', models.DecimalField(null=True, max_digits=4, decimal_places=2, blank=True)),
                ('maintainer', models.CharField(max_length=50)),
                ('description', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(null=True)),
                ('updated_at', models.DateTimeField(null=True)),
                ('external_url', models.CharField(max_length=255, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
