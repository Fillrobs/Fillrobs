# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-07-13 18:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vcloud_director', '0007_auto_20180712_1712'),
    ]

    operations = [
        migrations.AddField(
            model_name='vcddisk',
            name='independent_disk_href',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
