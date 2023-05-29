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
            name='XenNetwork',
            fields=[
                ('resourcenetwork_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='resourcehandlers.ResourceNetwork', on_delete=models.CASCADE)),
                ('uuid', models.CharField(verbose_name='Unique Identifier', max_length=50, null=True, editable=False, blank=True)),
            ],
            options={
                'verbose_name': 'Xen network',
            },
            bases=('resourcehandlers.resourcenetwork',),
        ),
        migrations.CreateModel(
            name='XenOSBuildAttribute',
            fields=[
                ('osbuildattribute_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='externalcontent.OSBuildAttribute', on_delete=models.CASCADE)),
                ('template_name', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name': 'Xen OS Build Attribute',
            },
            bases=('externalcontent.osbuildattribute',),
        ),
        migrations.CreateModel(
            name='XenResourceHandler',
            fields=[
                ('resourcehandler_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='resourcehandlers.ResourceHandler', on_delete=models.CASCADE)),
                ('default_sr', models.CharField(max_length=100, verbose_name='Default Storage Repository', blank=True)),
                ('template_filter_regex', models.CharField(max_length=50, null=True, verbose_name='Template Filter Regex', blank=True)),
                ('networks', models.ManyToManyField(to='xen.XenNetwork', null=True, blank=True)),
                ('os_build_attributes', models.ManyToManyField(to='xen.XenOSBuildAttribute', null=True, blank=True)),
            ],
            options={
                'verbose_name': 'Xen resource handler',
            },
            bases=('resourcehandlers.resourcehandler',),
        ),
    ]
