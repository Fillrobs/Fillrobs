# -*- coding: utf-8 -*-
# Generated by Django 1.11.22 on 2019-12-02 11:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('slayer', '0006_slayernetwork_is_public'),
    ]

    operations = [
        migrations.AddField(
            model_name='slayernetwork',
            name='datacenter',
            field=models.CharField(default='', max_length=30),
        ),
    ]