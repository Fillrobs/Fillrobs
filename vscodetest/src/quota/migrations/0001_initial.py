# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import quota.models
import quota.quota_set


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Quota',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('_unlimited_descendents', models.IntegerField(default=0)),
                ('total_used', models.DecimalField(default=0, max_digits=65, decimal_places=10)),
                ('used', models.DecimalField(default=0, max_digits=65, decimal_places=10)),
                ('delegated', models.DecimalField(default=0, max_digits=65, decimal_places=10)),
                ('limit', models.DecimalField(default=None, null=True, max_digits=65, decimal_places=10)),
                ('available', models.DecimalField(default=None, null=True, max_digits=65, decimal_places=10)),
                ('parent', models.ForeignKey(blank=True, to='quota.Quota', null=True, on_delete=models.SET_NULL)),
            ],
            options={
            },
            bases=(quota.models.BaseQuota, models.Model),
        ),
        migrations.CreateModel(
            name='ServerQuotaSet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cpu_cnt', models.ForeignKey(related_name='+', default=quota.models.create_empty_quota, blank=True, to='quota.Quota', null=True, on_delete=models.SET_NULL)),
                ('disk_size', models.ForeignKey(related_name='+', default=quota.models.create_empty_quota, blank=True, to='quota.Quota', null=True, on_delete=models.SET_NULL)),
                ('mem_size', models.ForeignKey(related_name='+', default=quota.models.create_empty_quota, blank=True, to='quota.Quota', null=True, on_delete=models.SET_NULL)),
                ('rate', models.ForeignKey(related_name='+', default=quota.models.create_empty_quota, blank=True, to='quota.Quota', null=True, on_delete=models.SET_NULL)),
                ('vm_cnt', models.ForeignKey(related_name='+', default=quota.models.create_empty_quota, blank=True, to='quota.Quota', null=True, on_delete=models.SET_NULL)),
            ],
            options={
            },
            bases=(quota.quota_set.QuotaSet, models.Model),
        ),
    ]
