# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-07-18 05:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vcloud_director', '0008_vcddisk_independent_disk_href'),
    ]

    operations = [
        migrations.AddField(
            model_name='vcdserverinfo',
            name='vapp_href',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
