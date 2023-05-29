# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('resourcehandlers', '0001_initial'),
        ('aws', '0001_initial'),
        ('infrastructure', '0002_serverexpireparameters_servernetworkcard_serversnapshot'),
    ]

    operations = [
        migrations.CreateModel(
            name='AWSHandler',
            fields=[
                ('resourcehandler_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='resourcehandlers.ResourceHandler', on_delete=models.CASCADE)),
                ('os_build_attributes', models.ManyToManyField(to='aws.AmazonMachineImage', null=True, blank=True)),
            ],
            options={
                'verbose_name': 'AWS resource handler',
            },
            bases=('resourcehandlers.resourcehandler',),
        ),
        migrations.CreateModel(
            name='AwsVpcSubnet',
            fields=[
                ('resourcenetwork_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='resourcehandlers.ResourceNetwork', on_delete=models.CASCADE)),
                ('availability_zone', models.CharField(max_length=30)),
                ('cidr_block', models.CharField(max_length=30)),
                ('default_for_az', models.BooleanField(default=None)),
                ('map_public_ip_on_launch', models.BooleanField(default=None)),
                ('vpc_id', models.CharField(max_length=30)),
            ],
            options={
                'verbose_name': 'AWS VPC subnet',
            },
            bases=('resourcehandlers.resourcenetwork',),
        ),
        migrations.CreateModel(
            name='EBSDisk',
            fields=[
                ('disk_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='infrastructure.Disk', on_delete=models.CASCADE)),
                ('availability_zone', models.CharField(max_length=50)),
            ],
            options={
                'abstract': False,
            },
            bases=('infrastructure.disk',),
        ),
        migrations.CreateModel(
            name='EC2ServerInfo',
            fields=[
                ('server', models.OneToOneField(primary_key=True, serialize=False, to='infrastructure.Server', on_delete=models.CASCADE)),
                ('ec2_region', models.CharField(max_length=100)),
                ('vpc_id', models.CharField(max_length=30, null=True, blank=True)),
                ('instance_id', models.CharField(max_length=100, null=True, blank=True)),
                ('instance_type', models.CharField(max_length=100, null=True, blank=True)),
                ('ip_address', models.CharField(max_length=20, null=True, blank=True)),
                ('elastic_ip', models.CharField(max_length=20, null=True, blank=True)),
                ('private_ip_address', models.CharField(max_length=20, null=True, blank=True)),
                ('public_dns_name', models.CharField(max_length=100, null=True, blank=True)),
                ('private_dns_name', models.CharField(max_length=100, null=True, blank=True)),
                ('availability_zone', models.CharField(max_length=100)),
                ('key_name', models.CharField(max_length=100)),
                ('security_groups_json', models.TextField(default='[]')),
                ('tags_json', models.TextField(default='{}')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
