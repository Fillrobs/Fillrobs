# -*- coding: utf-8 -*-
# Generated by Django 1.11.22 on 2019-10-22 19:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0016_auto_20191016_1541'),
    ]

    operations = [
        migrations.AddField(
            model_name='historymodel',
            name='rate_change',
            field=models.DecimalField(blank=True, decimal_places=10, max_digits=65, null=True, verbose_name='Change in Rate'),
        ),
    ]
