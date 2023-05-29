# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('externalcontent', '0002_auto_20160829_2059'),
        ('resourcehandlers', '0001_initial'),
        ('orders', '0001_initial'),
        ('accounts', '0003_auto_20160829_2059'),
        ('infrastructure', '0003_auto_20160829_2059'),
        ('servicecatalog', '0001_initial'),
        ('behavior_mapping', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='resourcepoolmapping',
            name='blueprint',
            field=models.ForeignKey(blank=True, to='servicecatalog.ServiceBlueprint', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='resourcepoolmapping',
            name='environment',
            field=models.ForeignKey(blank=True, to='infrastructure.Environment', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='resourcepoolmapping',
            name='group',
            field=models.ForeignKey(blank=True, to='accounts.Group', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='resourcepoolmapping',
            name='network',
            field=models.ForeignKey(blank=True, to='resourcehandlers.ResourceNetwork', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='resourcepoolmapping',
            name='os_family',
            field=models.ForeignKey(blank=True, to='externalcontent.OSFamily', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='resourcepoolmapping',
            name='pool',
            field=models.ForeignKey(to='infrastructure.ResourcePool', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='resourcepoolmapping',
            name='resource_handler',
            field=models.ForeignKey(blank=True, to='resourcehandlers.ResourceHandler', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='resourcepoolmapping',
            name='service_item',
            field=models.ForeignKey(blank=True, to='servicecatalog.ServiceItem', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='preconfigurationmapping',
            name='blueprint',
            field=models.ForeignKey(blank=True, to='servicecatalog.ServiceBlueprint', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='preconfigurationmapping',
            name='environment',
            field=models.ForeignKey(blank=True, to='infrastructure.Environment', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='preconfigurationmapping',
            name='group',
            field=models.ForeignKey(blank=True, to='accounts.Group', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='preconfigurationmapping',
            name='network',
            field=models.ForeignKey(blank=True, to='resourcehandlers.ResourceNetwork', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='preconfigurationmapping',
            name='options',
            field=models.ManyToManyField(to='orders.PreconfigurationValueSet', null=1),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='preconfigurationmapping',
            name='os_family',
            field=models.ForeignKey(blank=True, to='externalcontent.OSFamily', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='preconfigurationmapping',
            name='preconfiguration',
            field=models.ForeignKey(to='infrastructure.Preconfiguration', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='preconfigurationmapping',
            name='resource_handler',
            field=models.ForeignKey(blank=True, to='resourcehandlers.ResourceHandler', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='preconfigurationmapping',
            name='service_item',
            field=models.ForeignKey(blank=True, to='servicecatalog.ServiceItem', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='customfieldmapping',
            name='blueprint',
            field=models.ForeignKey(blank=True, to='servicecatalog.ServiceBlueprint', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='customfieldmapping',
            name='custom_field',
            field=models.ForeignKey(to='infrastructure.CustomField', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='customfieldmapping',
            name='default',
            field=models.ForeignKey(related_name='cfms_using_this_as_default_value', blank=True, to='orders.CustomFieldValue', null=True, on_delete=models.SET_NULL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='customfieldmapping',
            name='environment',
            field=models.ForeignKey(blank=True, to='infrastructure.Environment', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='customfieldmapping',
            name='group',
            field=models.ForeignKey(blank=True, to='accounts.Group', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='customfieldmapping',
            name='network',
            field=models.ForeignKey(blank=True, to='resourcehandlers.ResourceNetwork', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='customfieldmapping',
            name='options',
            field=models.ManyToManyField(to='orders.CustomFieldValue', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='customfieldmapping',
            name='os_family',
            field=models.ForeignKey(blank=True, to='externalcontent.OSFamily', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='customfieldmapping',
            name='resource_handler',
            field=models.ForeignKey(blank=True, to='resourcehandlers.ResourceHandler', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='customfieldmapping',
            name='service_item',
            field=models.ForeignKey(blank=True, to='servicecatalog.ServiceItem', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
    ]
