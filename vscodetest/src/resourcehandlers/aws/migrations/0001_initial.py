# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('externalcontent', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AmazonMachineImage',
            fields=[
                ('osbuildattribute_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='externalcontent.OSBuildAttribute', on_delete=models.CASCADE)),
                ('ami_id', models.CharField(max_length=100, null=True, blank=True)),
                ('architecture', models.CharField(default='x86_64', max_length=20, choices=[('i386', '32-bit'), ('x86_64', '64-bit')])),
                ('description', models.TextField(null=True, blank=True)),
                ('is_public', models.BooleanField(default=True)),
                ('name', models.CharField(max_length=255, null=True, blank=True)),
                ('owner_id', models.CharField(max_length=20, null=True, blank=True)),
                ('owner_alias', models.CharField(max_length=100, null=True, blank=True)),
                ('region', models.CharField(max_length=100)),
                ('root_device_type', models.CharField(default='ebs', max_length=20, choices=[('ebs', 'Elastic Block Store'), ('instance-store', 'Instance store')])),
                ('total_disk_size', models.DecimalField(help_text='Total size of all disks on this image in GB', null=True, max_digits=10, decimal_places=4, blank=True)),
            ],
            options={
                'verbose_name': 'Amazon Machine Image',
            },
            bases=('externalcontent.osbuildattribute',),
        ),
    ]
