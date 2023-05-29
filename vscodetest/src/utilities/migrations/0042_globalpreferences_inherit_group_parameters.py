# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-06-14 22:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('utilities', '0041_merge_20180515_1957'),
    ]

    operations = [
        migrations.AddField(
            model_name='globalpreferences',
            name='inherit_group_parameters',
            field=models.BooleanField(default=True, help_text='If enabled, parameters and preconfigurations set on parent groups will be inherited down to all their subgroups. This includes any options and constraints set on the parent group.', verbose_name='Inherit Group Parameters'),
        ),
    ]
