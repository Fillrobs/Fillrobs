# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-02-05 21:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('utilities', '0051_merge_20190102_1954'),
    ]

    operations = [
        migrations.AddField(
            model_name='globalpreferences',
            name='disabled_reports_list',
            field=models.TextField(blank=True, null=True),
        ),
    ]
