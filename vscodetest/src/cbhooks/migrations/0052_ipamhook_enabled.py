# -*- coding: utf-8 -*-
# Generated by Django 1.11.22 on 2019-08-16 17:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cbhooks', '0051_merge_20190815_1333'),
    ]

    operations = [
        migrations.AddField(
            model_name='ipamhook',
            name='enabled',
            field=models.BooleanField(default=False),
        ),
    ]
