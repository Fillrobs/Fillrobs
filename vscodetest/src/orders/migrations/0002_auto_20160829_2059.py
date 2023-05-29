# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('externalcontent', '0002_auto_20160829_2059'),
        ('containerorchestrators', '0001_initial'),
        ('resourcehandlers', '0001_initial'),
        ('orders', '0001_initial'),
        ('accounts', '0003_auto_20160829_2059'),
        ('infrastructure', '0003_auto_20160829_2059'),
        ('servicecatalog', '0001_initial'),
        ('utilities', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='provisionserverorderitem',
            name='service_item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='servicecatalog.ProvisionServerServiceItem', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='provisionnetworkorderitem',
            name='network_service_item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='servicecatalog.NetworkServiceItem', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='preconfigurationvalueset',
            name='applications',
            field=models.ManyToManyField(to='externalcontent.Application', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='preconfigurationvalueset',
            name='custom_field_values',
            field=models.ManyToManyField(to='orders.CustomFieldValue', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='preconfigurationvalueset',
            name='os_build',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, verbose_name='OS Build', blank=True, to='externalcontent.OSBuild', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='preconfigurationvalueset',
            name='preconfiguration',
            field=models.ForeignKey(to='infrastructure.Preconfiguration', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='orderitem',
            name='environment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='infrastructure.Environment', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='orderitem',
            name='order',
            field=models.ForeignKey(blank=True, to='orders.Order', null=True, on_delete=models.SET_NULL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='orderitem',
            name='parent_order_item',
            field=models.ForeignKey(blank=True, to='orders.OrderItem', null=True, on_delete=models.SET_NULL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='order',
            name='approved_by',
            field=models.ForeignKey(related_name='orders_approved', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='accounts.UserProfile', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='order',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='accounts.Group', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='order',
            name='owner',
            field=models.ForeignKey(related_name='orders_owned', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='accounts.UserProfile', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='installserviceorderitem',
            name='blueprint',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='servicecatalog.ServiceBlueprint', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='installserviceorderitem',
            name='custom_field_values',
            field=models.ManyToManyField(to='orders.CustomFieldValue', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='installserviceorderitem',
            name='service_items',
            field=models.ManyToManyField(to='servicecatalog.ServiceItem', through='orders.InstallServiceItemOptions'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='installserviceitemoptions',
            name='custom_field_values',
            field=models.ManyToManyField(to='orders.CustomFieldValue', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='installserviceitemoptions',
            name='environment',
            field=models.ForeignKey(to='infrastructure.Environment', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='installserviceitemoptions',
            name='isoi',
            field=models.ForeignKey(to='orders.InstallServiceOrderItem', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='installserviceitemoptions',
            name='os_build',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, verbose_name='OS Build', blank=True, to='externalcontent.OSBuild', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='installserviceitemoptions',
            name='preconfiguration_values',
            field=models.ManyToManyField(to='orders.PreconfigurationValueSet', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='installserviceitemoptions',
            name='service_item',
            field=models.ForeignKey(to='servicecatalog.ServiceItem', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='installpodorderitem',
            name='container_orchestrator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='containerorchestrators.ContainerOrchestrator', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='decomserverorderitem',
            name='servers',
            field=models.ManyToManyField(to='infrastructure.Server'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='customfieldvalue',
            name='field',
            field=models.ForeignKey(to='infrastructure.CustomField', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='customfieldvalue',
            name='ldap_value',
            field=models.ForeignKey(blank=True, to='utilities.LDAPUtility', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='customfieldvalue',
            name='network_value',
            field=models.ForeignKey(blank=1, to='resourcehandlers.ResourceNetwork', null=1, on_delete=models.CASCADE),
            preserve_default=True,
        ),
    ]
