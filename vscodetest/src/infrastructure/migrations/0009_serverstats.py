# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('infrastructure', '0008_diskstorage'),
    ]

    operations = [
        migrations.CreateModel(
            name='ServerStats',
            fields=[
                ('server', models.OneToOneField(related_name='stats', primary_key=True, serialize=False, to='infrastructure.Server', on_delete=models.CASCADE)),
                ('avg_cpu_last_year', models.DecimalField(null=True, verbose_name="Last year's average CPU utilization (%)", max_digits=5, decimal_places=2, blank=True)),
                ('avg_cpu_last_month', models.DecimalField(null=True, verbose_name="Last month's average CPU utilization (%)", max_digits=5, decimal_places=2, blank=True)),
                ('avg_cpu_last_week', models.DecimalField(null=True, verbose_name="Last week's average CPU utilization (%)", max_digits=5, decimal_places=2, blank=True)),
                ('avg_cpu_last_day', models.DecimalField(null=True, verbose_name='Last 24 hours average CPU utilization (%)', max_digits=5, decimal_places=2, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
