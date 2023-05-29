# -*- coding: utf-8 -*-
# Generated by Django 1.11.22 on 2019-12-27 10:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('slayer', '0010_auto_20191216_1920'),
    ]

    operations = [
        migrations.AlterField(
            model_name='slayerresourcehandler',
            name='networks',
            field=models.ManyToManyField(blank=True, related_name='resource_handler', to='slayer.SlayerNetwork'),
        ),
    ]
