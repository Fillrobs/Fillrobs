# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-05-01 18:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resourcehandlers', '0011_resourcehandler_enable_terminal_feature'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resourcetechnology',
            name='modulename',
            field=models.CharField(blank=1, max_length=100, verbose_name='Python module for interacting with this version of this resource management technology.'),
        ),
    ]
