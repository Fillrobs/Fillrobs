# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-05-08 12:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('infrastructure', '0032_lengthen_environment_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='serverstats',
            name='avg_cpu_last_week',
        ),
        migrations.AddField(
            model_name='serverstats',
            name='avg_cpu_last_hour',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name="Last hour's average CPU utilization (%)"),
        ),
    ]
