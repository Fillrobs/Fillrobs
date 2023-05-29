# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('externalcontent', '0002_auto_20160829_2059'),
        ('resourcehandlers', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SlayerNetwork',
            fields=[
                ('resourcenetwork_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='resourcehandlers.ResourceNetwork', on_delete=models.CASCADE)),
                ('uuid', models.CharField(default='', max_length=36)),
                ('cidr', models.CharField(default='29', max_length=30)),
            ],
            options={
                'verbose_name': 'IBM SoftLayer Network',
            },
            bases=('resourcehandlers.resourcenetwork',),
        ),
        migrations.CreateModel(
            name='SlayerOSBuildAttribute',
            fields=[
                ('osbuildattribute_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='externalcontent.OSBuildAttribute', on_delete=models.CASCADE)),
                ('template_name', models.CharField(max_length=100)),
                ('template_code', models.CharField(default='', max_length=100)),
                ('template_desc', models.CharField(default='', max_length=255)),
            ],
            options={
                'verbose_name': 'IBM SoftLayer OS Build Attribute',
            },
            bases=('externalcontent.osbuildattribute',),
        ),
        migrations.CreateModel(
            name='SlayerResourceHandler',
            fields=[
                ('resourcehandler_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='resourcehandlers.ResourceHandler', on_delete=models.CASCADE)),
                ('clusterName', models.CharField(default='', max_length=100)),
                ('networks', models.ManyToManyField(to='slayer.SlayerNetwork', null=True, blank=True)),
                ('os_build_attributes', models.ManyToManyField(to='slayer.SlayerOSBuildAttribute', null=True, blank=True)),
            ],
            options={
                'verbose_name': 'IBM SoftLayer Resource Handler',
            },
            bases=('resourcehandlers.resourcehandler',),
        ),
    ]
