# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2017-01-30 19:35
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('infrastructure', '0013_all_boolean_fields_optional'),
        ('cbhooks', '0007_sethideifdefaultvalue_20170123_1707'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customfield',
            name='hide_single_value',
        ),
    ]
