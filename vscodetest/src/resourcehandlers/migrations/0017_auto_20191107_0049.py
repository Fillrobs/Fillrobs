# -*- coding: utf-8 -*-
# Generated by Django 1.11.22 on 2019-11-07 00:49
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('resourcehandlers', '0016_auto_20191017_0101'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resourcenetwork',
            name='ipam_network',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='resource_networks', to='ipam.IPAMNetwork'),
        ),
    ]
