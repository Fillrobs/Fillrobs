# -*- coding: utf-8 -*-
# Generated by Django 1.11.22 on 2019-09-05 22:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('azure_arm', '0042_merge_20190709_1343'),
    ]

    operations = [
        migrations.CreateModel(
            name='AzureMeter',
            fields=[
                ('meter_id', models.UUIDField(primary_key=True, serialize=False)),
                ('meter_name', models.CharField(max_length=200)),
                ('meter_category', models.CharField(max_length=200)),
                ('meter_sub_category', models.CharField(max_length=200)),
                ('unit', models.CharField(max_length=100)),
                ('_meter_tags', models.CharField(max_length=100)),
                ('meter_region', models.CharField(max_length=100)),
                ('_meter_rates', models.CharField(max_length=300)),
                ('_effective_date', models.DateField()),
                ('included_quantity', models.IntegerField()),
            ],
        ),
    ]