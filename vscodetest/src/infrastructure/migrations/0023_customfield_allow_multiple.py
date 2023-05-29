# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-27 19:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('infrastructure', '0022_auto_20171012_1842'),
    ]

    operations = [
        migrations.AddField(
            model_name='customfield',
            name='allow_multiple',
            field=models.BooleanField(default=False, help_text='When enabled, a user can select multiple values when choosing between options for this parameter.', verbose_name='Allow multiple values'),
        ),
    ]