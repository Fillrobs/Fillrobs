# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import taggit.managers
import quota.models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('externalcontent', '0002_auto_20160829_2059'),
        ('orders', '0002_auto_20160829_2059'),
        ('provisionengines', '0001_initial'),
        ('resourcehandlers', '0001_initial'),
        ('accounts', '0003_auto_20160829_2059'),
        ('tags', '0001_initial'),
        ('infrastructure', '0004_auto_20160829_2059'),
        ('quota', '0001_initial'),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='server',
            name='tags',
            field=taggit.managers.TaggableManager(to='tags.CloudBoltTag', through='tags.TaggedItem', help_text='A comma-separated list of tags.', verbose_name='Tags'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='resourcepoolvalueset',
            name='applications',
            field=models.ManyToManyField(to='externalcontent.Application', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='resourcepoolvalueset',
            name='custom_field_values',
            field=models.ManyToManyField(to='orders.CustomFieldValue', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='resourcepoolvalueset',
            name='os_build',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, verbose_name='OS Build', blank=True, to='externalcontent.OSBuild', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='resourcepoolvalueset',
            name='resource_pool',
            field=models.ForeignKey(to='infrastructure.ResourcePool', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='resourcepoolvalueset',
            name='server',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='infrastructure.Server', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='resourcepool',
            name='custom_fields',
            field=models.ManyToManyField(to='infrastructure.CustomField', null=True, verbose_name='Provides Parameters', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='preconfiguration',
            name='custom_fields',
            field=models.ManyToManyField(to='infrastructure.CustomField', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='environment',
            name='custom_field_options',
            field=models.ManyToManyField(to='orders.CustomFieldValue', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='environment',
            name='custom_fields',
            field=models.ManyToManyField(to='infrastructure.CustomField', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='environment',
            name='data_center',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='infrastructure.DataCenter', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='environment',
            name='groups_served',
            field=models.ManyToManyField(to='accounts.Group', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='environment',
            name='preconfiguration_options',
            field=models.ManyToManyField(to='orders.PreconfigurationValueSet', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='environment',
            name='preconfigurations',
            field=models.ManyToManyField(to='infrastructure.Preconfiguration', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='environment',
            name='provision_engine',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='provisionengines.ProvisionEngine', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='environment',
            name='quota_set',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, default=quota.models.create_empty_quotaset, to='quota.ServerQuotaSet'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='environment',
            name='resource_handler',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='resourcehandlers.ResourceHandler', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='environment',
            name='resource_pool',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='infrastructure.ResourcePool', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='disk',
            name='real_type',
            field=models.ForeignKey(editable=False, to='contenttypes.ContentType', null=True, on_delete=models.SET_NULL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='disk',
            name='server',
            field=models.ForeignKey(related_name='disks', to='infrastructure.Server', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='customfield',
            name='namespace',
            field=models.ForeignKey(blank=True, to='infrastructure.Namespace', null=True, on_delete=models.SET_NULL),
            preserve_default=True,
        ),
    ]
