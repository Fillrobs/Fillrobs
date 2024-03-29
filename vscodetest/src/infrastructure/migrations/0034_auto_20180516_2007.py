# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-05-16 20:07
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('infrastructure', '0033_auto_20180508_1222'),
    ]

    operations = [
        migrations.CreateModel(
            name='ServerStatsSample',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('sample_type', models.CharField(choices=[('CPU', 'cpu'), ('MEM', 'mem'), ('DISK', 'disk'), ('NET', 'net')], max_length=30)),
                ('sample_period', models.CharField(choices=[('LAST_YEAR', 'last_year'), ('LAST_MONTH', 'last_month'), ('LAST_DAY', 'last_day'), ('LAST_HOUR', 'last_hour')], max_length=30)),
                ('value', models.IntegerField()),
                ('sort_order', models.IntegerField()),
            ],
            options={
                'ordering': ['sort_order'],
            },
        ),
        migrations.AddField(
            model_name='serverstats',
            name='last_refreshed',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='serverstatssample',
            name='server_stats',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='samples', to='infrastructure.ServerStats'),
        ),
    ]
