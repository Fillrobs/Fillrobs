# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('externalcontent', '0002_auto_20160829_2059'),
        ('resourcehandlers', '0001_initial'),
        ('infrastructure', '0002_serverexpireparameters_servernetworkcard_serversnapshot'),
        ('azure_arm', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AzureARMHandler',
            fields=[
                ('resourcehandler_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='resourcehandlers.ResourceHandler', on_delete=models.CASCADE)),
                ('client_id', models.CharField(help_text='Client ID for an Active Directory application', max_length=256, verbose_name='Client ID')),
                ('secret', models.CharField(help_text='Private key created for an Active Directory application', max_length=256)),
                ('tenant_id', models.CharField(help_text='Tenant ID for an Active Directory application', max_length=256, verbose_name='Tenant ID')),
            ],
            options={
                'verbose_name': 'Azure resource handler',
            },
            bases=('resourcehandlers.resourcehandler',),
        ),
        migrations.CreateModel(
            name='AzureARMImage',
            fields=[
                ('osbuildattribute_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='externalcontent.OSBuildAttribute', on_delete=models.CASCADE)),
                ('template_name', models.CharField(max_length=255)),
                ('publisher', models.CharField(max_length=255)),
                ('offer', models.CharField(max_length=255)),
                ('sku', models.CharField(max_length=255)),
                ('version', models.CharField(max_length=255)),
                ('location_availability', models.CharField(max_length=255)),
                ('total_disk_size', models.DecimalField(help_text='Total size of all disks on this image in GB', null=True, max_digits=10, decimal_places=4, blank=True)),
            ],
            options={
                'verbose_name': 'Image',
            },
            bases=('externalcontent.osbuildattribute',),
        ),
        migrations.CreateModel(
            name='AzureARMImageLocation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('image', models.ForeignKey(related_name='locations', to='azure_arm.AzureARMAvailableImage', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AzureARMServerInfo',
            fields=[
                ('server', models.OneToOneField(primary_key=True, serialize=False, to='infrastructure.Server', on_delete=models.CASCADE)),
                ('location', models.CharField(max_length=100)),
                ('resource_group', models.CharField(max_length=100)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AzureARMServerNetworkCard',
            fields=[
                ('servernetworkcard_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='infrastructure.ServerNetworkCard', on_delete=models.CASCADE)),
                ('enabled_ports', models.CharField(max_length=1024, blank=True)),
            ],
            options={
                'verbose_name': 'Azure ARM NIC',
            },
            bases=('infrastructure.servernetworkcard',),
        ),
        migrations.CreateModel(
            name='AzureARMSubnet',
            fields=[
                ('resourcenetwork_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='resourcehandlers.ResourceNetwork', on_delete=models.CASCADE)),
                ('cidr_block', models.CharField(max_length=30)),
                ('region', models.CharField(max_length=1024)),
                ('resource_group', models.CharField(max_length=1024)),
                ('parent_network', models.CharField(max_length=30)),
            ],
            options={
                'verbose_name': 'Azure Subnet',
            },
            bases=('resourcehandlers.resourcenetwork',),
        ),
        migrations.AddField(
            model_name='azurearmhandler',
            name='networks',
            field=models.ManyToManyField(to='azure_arm.AzureARMSubnet', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='azurearmhandler',
            name='os_build_attributes',
            field=models.ManyToManyField(to='azure_arm.AzureARMImage', null=True, blank=True),
            preserve_default=True,
        ),
    ]
