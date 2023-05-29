# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-24 20:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cbhooks', '0017_auto_20170727_1524'),
    ]

    operations = [
        migrations.AlterField(
            model_name='remotescripthook',
            name='run_with_sudo',
            field=models.BooleanField(default=False, help_text='Run this script with sudo on Unix-like servers.'),
        ),
    ]