# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):
    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='HistoryModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('event_message', models.TextField()),
                ('event_type', models.CharField(max_length=20)),
                ('action_time', models.DateTimeField(default=datetime.datetime.now)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EnvironmentHistory',
            fields=[
                ('historymodel_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='history.HistoryModel', on_delete=models.CASCADE)),
            ],
            options={
                'abstract': False,
            },
            bases=('history.historymodel',),
        ),
        migrations.CreateModel(
            name='LicensePoolHistory',
            fields=[
                ('historymodel_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='history.HistoryModel', on_delete=models.CASCADE)),
                ('used_count', models.PositiveIntegerField()),
                ('total_count', models.PositiveIntegerField()),
            ],
            options={
                'abstract': False,
            },
            bases=('history.historymodel',),
        ),
        migrations.CreateModel(
            name='ServerAggregatedTotals',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('servers', models.IntegerField(default=0)),
                ('cpus', models.IntegerField(default=0)),
                ('memory', models.IntegerField(default=0)),
                ('disk', models.IntegerField(default=0)),
                ('rate', models.DecimalField(default=0.0, max_digits=10, decimal_places=2)),
                ('aggregate_date', models.DateField()),
            ],
            options={
                'get_latest_by': 'aggregate_date',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GroupProfileTotals',
            fields=[
                ('serveraggregatedtotals_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='history.ServerAggregatedTotals', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=('history.serveraggregatedtotals',),
        ),
        migrations.CreateModel(
            name='GlobalAllocationTotals',
            fields=[
                ('serveraggregatedtotals_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='history.ServerAggregatedTotals', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=('history.serveraggregatedtotals',),
        ),
        migrations.CreateModel(
            name='ServerHistory',
            fields=[
                ('historymodel_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='history.HistoryModel', on_delete=models.CASCADE)),
                ('power_status', models.CharField(max_length=10)),
                ('cpu_cnt', models.IntegerField(default=0, null=True, blank=True)),
                ('disk_size', models.IntegerField(default=0, null=True, blank=True)),
                ('mem_size', models.DecimalField(default=0.0, null=True, max_digits=10, decimal_places=2, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('history.historymodel',),
        ),
        migrations.CreateModel(
            name='ServiceHistory',
            fields=[
                ('historymodel_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='history.HistoryModel', on_delete=models.CASCADE)),
                ('_service', models.TextField(help_text='JSON representation of the dictionary serialization of the service at a given time (event_time)')),
            ],
            options={
                'abstract': False,
            },
            bases=('history.historymodel',),
        ),
    ]
