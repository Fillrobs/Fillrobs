# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-06-20 23:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ipam', '0002_auto_20190605_2238'),
    ]

    operations = [
        migrations.AddField(
            model_name='ipamnetwork',
            name='_network_ref',
            field=models.CharField(default='', max_length=255),
        ),
    ]
