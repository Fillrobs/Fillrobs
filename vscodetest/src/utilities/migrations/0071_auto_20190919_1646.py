# -*- coding: utf-8 -*-
# Generated by Django 1.11.22 on 2019-09-19 16:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('utilities', '0070_merge_20190815_2030'),
    ]

    operations = [
        migrations.AlterField(
            model_name='globalpreferences',
            name='inactivity_timeout_minutes',
            field=models.IntegerField(blank=True, default=20, help_text='If set, log user out after this many minutes of inactivity.', null=True),
        ),
    ]